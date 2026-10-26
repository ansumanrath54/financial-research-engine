import json
from langchain_core.messages import HumanMessage
from app.models import AgentState, ResearchReport, UsageTelemetry
from app.llm_factory import (
    get_llm,
    get_provider_rate_card,
    extract_text_content,
    extract_token_counts,
)

llm = get_llm()
in_rate, out_rate = get_provider_rate_card()

def validator_node(state: AgentState) -> dict:
    tickers = state.get("tickers", ["NVDA", "MSFT"])
    t_a = tickers[0] if len(tickers) > 0 else "TICKER1"
    t_b = tickers[1] if len(tickers) > 1 else "TICKER2"

    market = state.get("market_data", {})
    sec = state.get("sec_data", {})
    telemetry_obj = UsageTelemetry(**state.get("telemetry", {}))

    prompt = f"""You are a certified financial auditor.
Synthesize the provided market data and SEC disclosures into a verified research report.
Respond ONLY with raw JSON matching this schema:
{{
  "tickers": ["{t_a}", "{t_b}"],
  "executive_summary": "1-2 sentence core institutional takeaway comparing operational leverage and valuation.",
  "metrics_table": [
    {{
      "metric": "Stock Price",
      "ticker_a_value": "{market.get(t_a, {}).get('stock_price', 'N/A')}",
      "ticker_b_value": "{market.get(t_b, {}).get('stock_price', 'N/A')}",
      "delta_commentary": "Current market valuation"
    }},
    {{
      "metric": "Operating Margin",
      "ticker_a_value": "{market.get(t_a, {}).get('operating_margin', 'N/A')}",
      "ticker_b_value": "{market.get(t_b, {}).get('operating_margin', 'N/A')}",
      "delta_commentary": "Operational margin spread"
    }},
    {{
      "metric": "Trailing P/E",
      "ticker_a_value": "{market.get(t_a, {}).get('trailing_pe', 'N/A')}",
      "ticker_b_value": "{market.get(t_b, {}).get('trailing_pe', 'N/A')}",
      "delta_commentary": "Earnings multiple comparison"
    }},
    {{
      "metric": "Free Cash Flow",
      "ticker_a_value": "{market.get(t_a, {}).get('free_cash_flow', 'N/A')}",
      "ticker_b_value": "{market.get(t_b, {}).get('free_cash_flow', 'N/A')}",
      "delta_commentary": "Operating liquidity"
    }},
    {{
      "metric": "CapEx Summary",
      "ticker_a_value": "{sec.get(t_a, {}).get('capex_summary', 'N/A')}",
      "ticker_b_value": "{sec.get(t_b, {}).get('capex_summary', 'N/A')}",
      "delta_commentary": "Capital infrastructure reinvestment rate"
    }}
  ],
  "risk_factors": [
    {{
      "ticker": "{t_a}",
      "risk_title": "{sec.get(t_a, {}).get('risk_title', 'Regulatory Headwinds')}",
      "summary": "{sec.get(t_a, {}).get('risk_summary', 'Disclosed supply chain or regulatory risks.')}",
      "citation": "{sec.get(t_a, {}).get('citation', 'SEC 10-Q/10-K')}"
    }},
    {{
      "ticker": "{t_b}",
      "risk_title": "{sec.get(t_b, {}).get('risk_title', 'Operational Headwinds')}",
      "summary": "{sec.get(t_b, {}).get('risk_summary', 'Disclosed competitive or macroeconomic risks.')}",
      "citation": "{sec.get(t_b, {}).get('citation', 'SEC 10-Q/10-K')}"
    }}
  ],
  "validation_status": "VERIFIED"
}}

Market Data Context: {json.dumps(market)}
SEC Context: {json.dumps(sec)}"""

    try:
        res = llm.invoke([HumanMessage(content=prompt)])
    except Exception as e:
        metrics = [
            ("Stock Price", "stock_price", "Retrieved market data"),
            ("Operating Margin", "operating_margin", "Retrieved market data"),
            ("Trailing P/E", "trailing_pe", "Retrieved market data"),
            ("Free Cash Flow", "free_cash_flow", "Retrieved market data"),
            ("CapEx Summary", "capex_summary", "Retrieved company data"),
        ]
        fallback = ResearchReport(
            tickers=tickers,
            executive_summary=(
                "Gemini report generation failed. Retrieved values are shown below "
                "without AI-generated comparative analysis."
            ),
            metrics_table=[
                {
                    "metric": label,
                    "ticker_a_value": str(market.get(t_a, {}).get(key, sec.get(t_a, {}).get(key, "N/A"))),
                    "ticker_b_value": str(market.get(t_b, {}).get(key, sec.get(t_b, {}).get(key, "N/A"))),
                    "delta_commentary": note,
                }
                for label, key, note in metrics
            ],
            risk_factors=[
                {
                    "ticker": ticker,
                    "risk_title": sec.get(ticker, {}).get("risk_title", "Risk data unavailable"),
                    "summary": sec.get(ticker, {}).get(
                        "risk_summary", "No filing risk summary was retrieved."
                    ),
                    "citation": sec.get(ticker, {}).get("citation", "N/A"),
                }
                for ticker in (t_a, t_b)
            ],
            validation_status="FLAGGED",
        ).model_dump()
        telemetry_obj.accumulate(0, 0, in_cost_per_m=in_rate, out_cost_per_m=out_rate)
        return {
            "final_report": fallback,
            "errors": [f"Report generation failed: {e}"],
            "validation_retryable": False,
            "telemetry": telemetry_obj.model_dump(),
            "active_worker": None
        }

    try:
        raw = extract_text_content(res.content).strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        validated = ResearchReport(**data).model_dump()
        errors = []
        in_tok, out_tok = extract_token_counts(res)
    except Exception as e:
        validated = None
        errors = [f"Report response validation failed: {str(e)}"]
        in_tok, out_tok = 200, 60

    telemetry_obj.accumulate(in_tok, out_tok, in_cost_per_m=in_rate, out_cost_per_m=out_rate)

    return {
        "final_report": validated,
        "errors": errors,
        "validation_retryable": bool(errors),
        "telemetry": telemetry_obj.model_dump(),
        "active_worker": None
    }