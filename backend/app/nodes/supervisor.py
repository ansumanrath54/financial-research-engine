import json
from langchain_core.messages import HumanMessage
from app.models import AgentState, UsageTelemetry
from app.llm_factory import (
    get_llm,
    get_provider_rate_card,
    extract_text_content,
    extract_token_counts,
)

llm = get_llm()
in_rate, out_rate = get_provider_rate_card()

def supervisor_node(state: AgentState) -> dict:
    query = state["user_query"]
    prompt = f"""You are the Supervisor of an autonomous financial research platform.
Analyze the user's research request. Identify the target stock tickers and produce an execution task plan.
User query: "{query}"

Respond ONLY with valid JSON (no markdown backticks):
{{
  "tickers": ["TICKER1", "TICKER2"],
  "tasks": ["Execute deterministic market metrics query", "Retrieve dynamic SEC EDGAR disclosures"]
}}"""

    telemetry_obj = UsageTelemetry(**state.get("telemetry", {}))

    try:
        res = llm.invoke([HumanMessage(content=prompt)])
        raw = extract_text_content(res.content).strip()
        if raw.startswith("```"):
            raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        data = json.loads(raw)
        tickers = data.get("tickers", ["NVDA", "MSFT"])
        plan = data.get("tasks", [])
        in_tok, out_tok = extract_token_counts(res)
    except Exception:
        tickers = ["NVDA", "MSFT"]
        plan = ["Fetch market metrics", "Retrieve SEC filings"]
        in_tok, out_tok = 120, 40

    telemetry_obj.accumulate(in_tok, out_tok, in_cost_per_m=in_rate, out_cost_per_m=out_rate)

    return {
        "tickers": tickers,
        "plan": plan,
        "active_worker": "market_worker",
        "telemetry": telemetry_obj.model_dump(),
        "iteration_count": state.get("iteration_count", 0) + 1
    }