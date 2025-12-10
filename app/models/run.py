"""Models representing workflow run metadata and logging."""

from __future__ import annotations

from typing import Any, Literal

from enum import Enum

from pydantic import BaseModel, Field

from .state import WorkflowState


class ExecutionStepLog(BaseModel):
    """Log entry for a node execution step."""

    node_name: str
    status: Literal["pending", "running", "success", "error"]
    message: str | None = None
    state_snapshot: dict[str, Any] | None = None


class RunStatus(str, Enum):
    """Possible statuses for a workflow run."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RunRecord(BaseModel):
    """Represents a workflow run instance."""

    id: str
    graph_id: str
    status: RunStatus
    current_node: str | None
    state: WorkflowState
    log: list[ExecutionStepLog] = Field(default_factory=list)


class RunRequest(BaseModel):
    """Request payload to start a workflow run."""

    graph_id: str
    initial_state: dict[str, Any]


class RunResponse(BaseModel):
    """Response payload after running a workflow."""

    run_id: str
    final_state: dict[str, Any]
    log: list[ExecutionStepLog]


