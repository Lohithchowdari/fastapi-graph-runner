"""Rule-based summarization workflow tools."""

from __future__ import annotations

from typing import List

from app.core.registry import ToolRegistry
from app.models.state import WorkflowState


def _chunk_text(text: str, chunk_size: int) -> List[str]:
    """Split text into roughly chunk_size character chunks on whitespace."""
    words = text.split()
    chunks: List[str] = []
    current = ""

    for word in words:
        if len(current) + len(word) + 1 > chunk_size and current:
            chunks.append(current.strip())
            current = ""
        current += word + " "
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text]


def split_text(state: WorkflowState) -> WorkflowState:
    """Split input text into chunks."""
    text = state.data.get("input_text", "")
    chunk_size = int(state.data.get("chunk_size", 200))
    state.data["chunks"] = _chunk_text(text, chunk_size)
    return state


def generate_chunk_summaries(state: WorkflowState) -> WorkflowState:
    """Create naive summaries for each chunk."""
    chunks: List[str] = state.data.get("chunks", [])
    summaries: List[str] = []
    for chunk in chunks:
        # simple heuristic: first sentence or first 30 words
        sentence_end = chunk.find(".")
        if 0 < sentence_end < 200:
            summaries.append(chunk[: sentence_end + 1])
        else:
            summaries.append(" ".join(chunk.split()[:30]))
    state.data["chunk_summaries"] = summaries
    return state


def merge_summaries(state: WorkflowState) -> WorkflowState:
    """Merge chunk summaries into a single text."""
    chunk_summaries: List[str] = state.data.get("chunk_summaries", [])
    merged = " | ".join(chunk_summaries)
    state.data["merged_summary"] = merged
    return state


def refine_summary(state: WorkflowState) -> WorkflowState:
    """Refine merged summary to respect max length and set branch choice."""
    summary = state.data.get("merged_summary", "")
    max_length = int(state.data.get("max_length", 400))
    refine_count = int(state.meta.get("refine_count", 0))

    if len(summary) > max_length and refine_count < 3:
        summary = summary[:max_length]
        refine_count += 1
        state.meta["branch_choice"] = "too_long"
    else:
        state.meta["branch_choice"] = "ok"

    state.meta["refine_count"] = refine_count
    state.data["final_summary"] = summary
    return state


def register_summarization_tools(registry: ToolRegistry) -> None:
    """Register summarization tools with the provided registry."""
    registry.register("split_text", split_text)
    registry.register("generate_chunk_summaries", generate_chunk_summaries)
    registry.register("merge_summaries", merge_summaries)
    registry.register("refine_summary", refine_summary)


