"""Integration-style tests for FastAPI routes."""

from fastapi.testclient import TestClient

from app.main import DEFAULT_SUMMARIZATION_GRAPH_ID, app


def test_run_endpoint_returns_summary():
    with TestClient(app) as client:
        graph_id = client.app.state.default_graph_id or DEFAULT_SUMMARIZATION_GRAPH_ID
        payload = {
            "graph_id": graph_id,
            "initial_state": {
                "input_text": (
                    "FastAPI makes it easy to build APIs quickly. "
                    "This example shows a simple workflow engine."
                ),
                "chunk_size": 50,
                "max_length": 120,
            },
        }

        response = client.post("/graph/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "final_summary" in data["final_state"]
        assert data["run_id"]


