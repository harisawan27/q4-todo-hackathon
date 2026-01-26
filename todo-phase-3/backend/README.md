# Todo AI Chatbot - Backend

Python FastAPI backend with OpenAI agent integration and MCP tools for task management.

## Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
DATABASE_URL=postgresql://user:password@host:5432/database
OPENAI_API_KEY=sk-your-openai-api-key
```

### 4. Run the Server

```bash
uvicorn app.main:app --reload --port 8001
```

The server will be available at http://localhost:8001

## API Documentation

Interactive API docs are available at:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry
│   ├── config.py        # Pydantic settings
│   ├── database.py      # SQLModel database setup
│   ├── models/          # Data models
│   │   ├── task.py      # Task model (Phase 2 replica)
│   │   ├── conversation.py
│   │   └── message.py
│   ├── mcp/             # MCP tools
│   │   ├── server.py    # MCP server init
│   │   └── tools.py     # Task management tools
│   ├── agent/           # OpenAI agent
│   │   └── runner.py    # Agent execution logic
│   └── api/             # API routes
│       └── chat.py      # Chat endpoint
├── tests/               # Test suite
│   ├── conftest.py
│   ├── test_mcp_tools.py
│   └── test_api.py
├── requirements.txt
└── .env.example
```

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=app --cov-report=html
```

## MCP Tools

The following tools are available to the AI agent:

| Tool | Description |
|------|-------------|
| `list_tasks` | List user's tasks (filter by status) |
| `add_task` | Create a new task |
| `complete_task` | Mark a task as done |
| `update_task` | Update task title/description |
| `delete_task` | Remove a task |
| `find_task_by_title` | Search for tasks by title |

## Database

The backend connects to the same Neon PostgreSQL database as Phase 2. Tables:

- `tasks` - Shared with Phase 2 (exact schema match)
- `conversations` - Phase 3 only
- `messages` - Phase 3 only
