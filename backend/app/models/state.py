from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

class AgentState(TypedDict):
    thread_id: str
    user_query: str
    tickers: List[str]
    plan: List[str]
    market_data: Dict[str, Any]
    sec_data: Dict[str, Any]
    final_report: Optional[Dict[str, Any]]
    telemetry: Dict[str, Any]
    errors: Annotated[List[str], operator.add]
    iteration_count: int
    validation_retryable: bool
    active_worker: Optional[str]