"""Graph definition models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class NodeConfig(BaseModel):
    """Configuration for a node in the workflow graph."""

    name: str = Field(..., description="Logical name of the node.")
    func_name: str = Field(..., description="Registered tool/function to execute.")
    next: Optional[str] = Field(
        default=None, description="Default next node to execute after this one."
    )
    branch_conditions: Optional[dict[str, Optional[str]]] = Field(
        default=None,
        description=(
            "Optional branching map: choice key -> next node name. "
            "Branching choice resolved by the engine."
        ),
    )


class GraphDefinition(BaseModel):
    """Represents a workflow graph definition."""

    id: str
    nodes: dict[str, NodeConfig]
    entrypoint: str


class CreateGraphRequest(BaseModel):
    """Request payload to create a new graph definition."""

    nodes: dict[str, NodeConfig]
    entrypoint: str


class CreateGraphResponse(BaseModel):
    """Response payload containing the created graph identifier."""

    graph_id: str


