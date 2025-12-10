"""Simple tool registry to hold callable workflow functions."""

from __future__ import annotations

from typing import Callable

from app.models.state import WorkflowState

ToolFunc = Callable[[WorkflowState], WorkflowState]


class ToolRegistry:
    """Registry for workflow tools."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolFunc] = {}

    def register(self, name: str, func: ToolFunc) -> None:
        """Register a tool function under a name."""
        self._tools[name] = func

    def get(self, name: str) -> ToolFunc:
        """Fetch a registered tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool {name} not registered")
        return self._tools[name]

    def list_tools(self) -> dict[str, str]:
        """Return a mapping of tool names to their docstring or function name."""
        return {
            name: (func.__doc__ or func.__name__)
            for name, func in self._tools.items()
        }


