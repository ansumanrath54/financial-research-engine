import json
import asyncio
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.auth import get_current_user, router as auth_router, validate_auth_config
from app.db import (
    User,
    close_db,
    get_all_sessions,
    get_session_by_id,
    init_db,
    save_session,
    session_thread_id_conflicts,
)
from app.graph import get_compiled_graph, close_graph_pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_auth_config()
    await init_db()
    await get_compiled_graph()
    yield
    await close_db()
    await close_graph_pool()

app = FastAPI(title="ApexAlpha Financial Research Engine", lifespan=lifespan)
app.include_router(auth_router)

# Allow React dev server on port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResearchRequest(BaseModel):
    thread_id: str = Field(min_length=1, max_length=128)
    query: str = Field(min_length=1, max_length=10000)

@app.get("/api/sessions")
async def list_sessions(current_user: User = Depends(get_current_user)):
    return await get_all_sessions(current_user.id)

@app.get("/api/sessions/{thread_id}")
async def get_session(thread_id: str, current_user: User = Depends(get_current_user)):
    session = await get_session_by_id(thread_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/api/research/stream")
async def stream_research(
    req: ResearchRequest,
    current_user: User = Depends(get_current_user),
):
    thread_id = req.thread_id
    if await session_thread_id_conflicts(thread_id, current_user.id):
        raise HTTPException(status_code=409, detail="Thread ID is already in use")

    config = {"configurable": {"thread_id": f"user-{current_user.id}-{thread_id}"}}
    graph = await get_compiled_graph()

    initial_state = {
        "thread_id": thread_id,
        "user_query": req.query,
        "tickers": [],
        "plan": [],
        "market_data": {},
        "sec_data": {},
        "final_report": None,
        "telemetry": {"input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0, "api_calls": 0},
        "errors": [],
        "iteration_count": 0,
        "validation_retryable": False,
        "active_worker": "supervisor"
    }

    async def event_generator():
        last_state = {}
        yield f"data: {json.dumps({'status': 'started'})}\n\n"
        async for event in graph.astream(initial_state, config=config):
            for node_name, state_chunk in event.items():
                last_state.update(state_chunk)
                payload = {
                    "node": node_name,
                    "active_worker": state_chunk.get("active_worker"),
                    "plan": state_chunk.get("plan"),
                    "telemetry": state_chunk.get("telemetry"),
                    "errors": state_chunk.get("errors"),
                    "final_report": state_chunk.get("final_report")
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0.04)

        if last_state.get("final_report"):
            tickers = last_state.get("tickers", ["Equity"])
            title = f"{' vs '.join(tickers)} Research"
            await save_session(
                user_id=current_user.id,
                thread_id=thread_id,
                title=title,
                query=req.query,
                tickers=tickers,
                report=last_state.get("final_report"),
                telemetry=last_state.get("telemetry")
            )

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)