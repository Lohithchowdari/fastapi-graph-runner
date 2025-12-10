"""Simple in-memory storage for graphs and runs."""

from __future__ import annotations

from typing import Dict

from app.models.graph import GraphDefinition
from app.models.run import RunRecord


class GraphStore:
    """In-memory store for graph definitions."""

    def __init__(self) -> None:
        self.graphs: Dict[str, GraphDefinition] = {}

    def save(self, graph: GraphDefinition) -> None:
        """Persist a graph definition."""
        self.graphs[graph.id] = graph

    def get(self, graph_id: str) -> GraphDefinition:
        """Retrieve a graph definition by id."""
        if graph_id not in self.graphs:
            raise KeyError(f"Graph {graph_id} not found")
        return self.graphs[graph_id]


class RunStore:
    """In-memory store for workflow runs."""

    def __init__(self) -> None:
        self.runs: Dict[str, RunRecord] = {}

    def create(self, run: RunRecord) -> None:
        """Persist a new run record."""
        self.runs[run.id] = run

    def get(self, run_id: str) -> RunRecord:
        """Retrieve a run record."""
        if run_id not in self.runs:
            raise KeyError(f"Run {run_id} not found")
        return self.runs[run_id]

    def update(self, run: RunRecord) -> None:
        """Update an existing run record."""
        self.runs[run.id] = run


