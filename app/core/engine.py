"""Workflow engine implementation."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from app.core.registry import ToolRegistry
from app.core.storage import GraphStore, RunStore
from app.models.graph import CreateGraphRequest, GraphDefinition, NodeConfig
from app.models.run import ExecutionStepLog, RunRecord, RunStatus
from app.models.state import WorkflowState


class WorkflowEngine:
    """Core workflow engine handling graph creation and execution."""

    def __init__(
        self,
        graph_store: GraphStore,
        run_store: RunStore,
        tool_registry: ToolRegistry,
    ) -> None:
        self.graph_store = graph_store
        self.run_store = run_store
        self.tool_registry = tool_registry

    def create_graph(self, req: CreateGraphRequest) -> GraphDefinition:
        """Create and persist a new graph definition."""
        graph_id = str(uuid4())
        graph = GraphDefinition(id=graph_id, nodes=req.nodes, entrypoint=req.entrypoint)
        self.graph_store.save(graph)
        return graph

    def start_run(self, graph_id: str, initial_state: dict[str, Any]) -> RunRecord:
        """Start execution of a graph with an initial state."""
        graph = self.graph_store.get(graph_id)
        run_id = str(uuid4())
        run = RunRecord(
            id=run_id,
            graph_id=graph.id,
            status=RunStatus.RUNNING,
            current_node=graph.entrypoint,
            state=WorkflowState(data=initial_state, meta={}),
            log=[],
        )
        self.run_store.create(run)
        return self._execute_run(run_id)

    def _execute_run(self, run_id: str) -> RunRecord:
        """Execute a workflow run synchronously."""
        while True:
            run = self.run_store.get(run_id)
            graph = self.graph_store.get(run.graph_id)

            if run.current_node is None:
                if run.status != RunStatus.FAILED:
                    run.status = RunStatus.COMPLETED
                self.run_store.update(run)
                break

            node_config = graph.nodes.get(run.current_node)
            if node_config is None:
                run.log.append(
                    ExecutionStepLog(
                        node_name=run.current_node,
                        status="error",
                        message="Node not found",
                        state_snapshot=run.state.dict(),
                    )
                )
                run.status = RunStatus.FAILED
                run.current_node = None
                self.run_store.update(run)
                break

            run.log.append(
                ExecutionStepLog(
                    node_name=node_config.name,
                    status="running",
                    state_snapshot=run.state.model_dump(),
                )
            )

            try:
                tool = self.tool_registry.get(node_config.func_name)
                new_state = tool(run.state)
                run.state = new_state
                run.log.append(
                    ExecutionStepLog(
                        node_name=node_config.name,
                        status="success",
                        state_snapshot=run.state.model_dump(),
                    )
                )

                next_node = (
                    self._resolve_branch(node_config, run.state)
                    if node_config.branch_conditions
                    else node_config.next
                )

                if next_node is None:
                    run.current_node = None
                    run.status = RunStatus.COMPLETED
                    self.run_store.update(run)
                    break

                run.current_node = next_node
                self.run_store.update(run)
                continue

            except Exception as exc:  # pragma: no cover - defensive
                run.log.append(
                    ExecutionStepLog(
                        node_name=node_config.name,
                        status="error",
                        message=str(exc),
                        state_snapshot=run.state.model_dump(),
                    )
                )
                run.status = RunStatus.FAILED
                run.current_node = None
                self.run_store.update(run)
                break

        return self.run_store.get(run_id)

    def _resolve_branch(
        self, node: NodeConfig, state: WorkflowState
    ) -> str | None:
        """Resolve branching using state.meta['branch_choice'] and node conditions."""
        if not node.branch_conditions:
            return node.next

        choice = state.meta.get("branch_choice")
        if choice is None:
            return node.next
        return node.branch_conditions.get(choice, node.next)

    def get_run(self, run_id: str) -> RunRecord:
        """Fetch a run by id."""
        return self.run_store.get(run_id)


