# Workflow Engine Assignment
[Open Swagger UI](http://127.0.0.1:8000/docs#/)

## Project Overview
This project implements a minimal workflow/graph engine using FastAPI. Nodes are Python functions operating on a shared state; edges define execution order with support for branching and looping through state metadata. The engine provides APIs to create graphs, run them, and inspect run state.

## Tech Stack
- Python
- FastAPI
- Pydantic
- In-memory storage

## How to Run
1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Start the API:
   ```
   uvicorn app.main:app --reload
   ```
3. Example `curl` to run the default summarization workflow:
   ```
   curl -X POST http://localhost:8000/graph/run \
     -H "Content-Type: application/json" \
     -d '{
       "graph_id": "<DEFAULT_SUMMARIZATION_GRAPH_ID>",
       "initial_state": {
         "input_text": "long text here...",
         "chunk_size": 200,
         "max_length": 400
       }
     }'
   ```

## Engine Capabilities
- Nodes as Python functions (tools) registered in a registry.
- Shared state (dict/Pydantic) passed between nodes.
- Branching via `branch_conditions` plus `state.meta["branch_choice"]`.
- Looping via repeated branching with a refine counter safeguard.
- Tool registry for reusable functions.

## Possible Improvements
- Async execution of long-running steps or background tasks.
- WebSocket streaming of step-by-step logs.
- Persistent storage using SQLite/Postgres.
- Graph validation and visualization.
- Richer DSL/JSON format for graph definitions.


