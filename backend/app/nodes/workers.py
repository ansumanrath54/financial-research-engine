from app.models import AgentState
from app.tools import fetch_market_metrics, fetch_sec_filing_data
from concurrent.futures import ThreadPoolExecutor

def market_worker_node(state: AgentState) -> dict:
    tickers = state.get("tickers", ["NVDA", "MSFT"])
    with ThreadPoolExecutor(max_workers=max(1, min(len(tickers), 4))) as executor:
        results = dict(zip(tickers, executor.map(fetch_market_metrics, tickers)))
    return {
        "market_data": results
    }

def sec_worker_node(state: AgentState) -> dict:
    tickers = state.get("tickers", ["NVDA", "MSFT"])
    with ThreadPoolExecutor(max_workers=max(1, min(len(tickers), 4))) as executor:
        results = dict(zip(tickers, executor.map(fetch_sec_filing_data, tickers)))
    return {
        "sec_data": results
    }