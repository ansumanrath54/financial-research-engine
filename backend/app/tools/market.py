import yfinance as yf
from typing import Dict, Any

def fetch_market_metrics(ticker: str) -> Dict[str, Any]:
    clean = ticker.upper().strip()
    try:
        t = yf.Ticker(clean)
        info = t.info
        price = info.get("currentPrice") or info.get("regularMarketPrice") or 0.0
        pe = info.get("trailingPE") or info.get("forwardPE") or 0.0
        margin = info.get("operatingMargins") or 0.0
        fcf = info.get("freeCashflow") or 0.0
        rev_growth = info.get("revenueGrowth") or 0.0

        return {
            "ticker": clean,
            "status": "SUCCESS",
            "stock_price": f"${price:,.2f}" if price else "N/A",
            "trailing_pe": f"{pe:.1f}x" if pe else "N/A",
            "operating_margin": f"{margin * 100:.1f}%" if margin else "N/A",
            "free_cash_flow": f"${fcf / 1e9:.2f}B" if fcf else "N/A",
            "revenue_growth": f"{rev_growth * 100:.1f}%" if rev_growth else "N/A"
        }
    except Exception as e:
        return {
            "ticker": clean,
            "status": "FALLBACK",
            "error": str(e),
            "stock_price": "N/A",
            "trailing_pe": "N/A",
            "operating_margin": "N/A",
            "free_cash_flow": "N/A",
            "revenue_growth": "N/A"
        }