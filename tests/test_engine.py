"""Unit tests for the workflow engine."""

from app.core.engine import WorkflowEngine
from app.core.registry import ToolRegistry
from app.core.storage import GraphStore, RunStore
from app.models.graph import CreateGraphRequest, NodeConfig
from app.models.state import WorkflowState


def test_engine_simple_run():
    """Ensure a simple linear graph executes and updates state."""
    graph_store = GraphStore()
    run_store = RunStore()
    registry = ToolRegistry()

    def step_a(state: WorkflowState) -> WorkflowState:
        state.data["count"] = state.data.get("count", 0) + 1
        return state

    def step_b(state: WorkflowState) -> WorkflowState:
        state.data["count"] = state.data.get("count", 0) + 1
        return state

    registry.register("step_a", step_a)
    registry.register("step_b", step_b)

    engine = WorkflowEngine(graph_store, run_store, registry)

    graph = engine.create_graph(
        CreateGraphRequest(
            nodes={
                "a": NodeConfig(name="a", func_name="step_a", next="b"),
                "b": NodeConfig(name="b", func_name="step_b", next=None),
            },
            entrypoint="a",
        )
    )

    run = engine.start_run(graph.id, {"count": 0})

    assert run.state.data["count"] == 2
    assert run.status == "COMPLETED"
    assert run.current_node is None
    assert len(run.log) >= 2


