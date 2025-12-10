"""FastAPI routes for graph operations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.core.engine import WorkflowEngine
from app.models.graph import CreateGraphRequest, CreateGraphResponse, GraphDefinition
from app.models.run import RunRequest, RunResponse

router = APIRouter(prefix="/graph", tags=["graph"])


def get_engine(request: Request) -> WorkflowEngine:
    """Resolve the workflow engine from the FastAPI app state."""
    engine: WorkflowEngine = request.app.state.engine
    return engine


@router.post("/create", response_model=CreateGraphResponse)
async def create_graph(
    req: CreateGraphRequest, engine: WorkflowEngine = Depends(get_engine)
) -> CreateGraphResponse:
    """Create a new graph definition."""
    graph: GraphDefinition = engine.create_graph(req)
    return CreateGraphResponse(graph_id=graph.id)


@router.post("/run", response_model=RunResponse)
async def run_graph(
    req: RunRequest, engine: WorkflowEngine = Depends(get_engine)
) -> RunResponse:
    """Run a graph with the provided initial state."""
    run = engine.start_run(req.graph_id, req.initial_state)
    return RunResponse(run_id=run.id, final_state=run.state.data, log=run.log)


@router.get("/state/{run_id}")
async def get_run_state(
    run_id: str, engine: WorkflowEngine = Depends(get_engine)
) -> dict:
    """Retrieve the state of an ongoing or completed run."""
    run = engine.get_run(run_id)
    return {
        "run_id": run.id,
        "graph_id": run.graph_id,
        "status": run.status,
        "current_node": run.current_node,
        "state": run.state.data,
        "log": run.log,
    }


