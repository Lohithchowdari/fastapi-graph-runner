"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.routes_graph import router as graph_router
from app.core.engine import WorkflowEngine
from app.core.registry import ToolRegistry
from app.core.storage import GraphStore, RunStore
from app.models.graph import CreateGraphRequest, NodeConfig
from app.workflows.summarization import register_summarization_tools

graph_store = GraphStore()
run_store = RunStore()
tool_registry = ToolRegistry()
register_summarization_tools(tool_registry)
engine = WorkflowEngine(graph_store, run_store, tool_registry)

DEFAULT_SUMMARIZATION_GRAPH_ID: str | None = None

app = FastAPI(title="Workflow Engine")
app.state.engine = engine
app.state.default_graph_id = None


def create_default_summarization_graph() -> str:
    """Create and register the default summarization workflow graph."""
    request = CreateGraphRequest(
        nodes={
            "split": NodeConfig(
                name="split",
                func_name="split_text",
                next="summarize",
            ),
            "summarize": NodeConfig(
                name="summarize",
                func_name="generate_chunk_summaries",
                next="merge",
            ),
            "merge": NodeConfig(
                name="merge",
                func_name="merge_summaries",
                next="refine",
            ),
            "refine": NodeConfig(
                name="refine",
                func_name="refine_summary",
                next=None,
                branch_conditions={"too_long": "refine", "ok": None},
            ),
        },
        entrypoint="split",
    )
    graph = engine.create_graph(request)
    return graph.id


@app.on_event("startup")
async def _startup() -> None:
    """Initialize default resources."""
    global DEFAULT_SUMMARIZATION_GRAPH_ID
    DEFAULT_SUMMARIZATION_GRAPH_ID = create_default_summarization_graph()
    app.state.engine = engine
    app.state.default_graph_id = DEFAULT_SUMMARIZATION_GRAPH_ID


@app.get("/")
async def root() -> dict[str, str | None]:
    """Health endpoint."""
    return {
        "message": "Workflow engine up",
        "default_graph_id": DEFAULT_SUMMARIZATION_GRAPH_ID,
    }


app.include_router(graph_router)


