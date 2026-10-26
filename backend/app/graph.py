import os
from psycopg_pool import AsyncConnectionPool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.models import AgentState
from app.nodes import (
    supervisor_node,
    market_worker_node,
    sec_worker_node,
    validator_node
)

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@localhost:5432/financial_research"
)

def evaluate_validation(state: AgentState) -> str:
    if state.get("validation_retryable", False) and state.get("iteration_count", 0) < 2:
        return "supervisor"
    return END

def create_raw_workflow() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("market_worker", market_worker_node)
    workflow.add_node("sec_worker", sec_worker_node)
    workflow.add_node("validator", validator_node)

    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "market_worker")
    workflow.add_edge("supervisor", "sec_worker")
    workflow.add_edge("market_worker", "validator")
    workflow.add_edge("sec_worker", "validator")

    workflow.add_conditional_edges(
        "validator",
        evaluate_validation,
        {
            "supervisor": "supervisor",
            END: END
        }
    )
    return workflow

_compiled_graph = None
_pool = None

async def get_compiled_graph():
    global _compiled_graph, _pool
    if _compiled_graph is None:
        _pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            max_size=10,
            kwargs={"autocommit": True, "prepare_threshold": 0}
        )
        await _pool.open()
        
        checkpointer = AsyncPostgresSaver(_pool)
        await checkpointer.setup()
        
        workflow = create_raw_workflow()
        _compiled_graph = workflow.compile(checkpointer=checkpointer)
        
    return _compiled_graph

async def close_graph_pool():
    global _pool, _compiled_graph
    if _pool is not None:
        await _pool.close()
        _pool = None
        _compiled_graph = None