# Todo AI Chatbot (Phase 3)

A conversational AI interface for managing tasks using natural language. This chatbot connects to the same database as Phase 2, enabling seamless task management across both interfaces.

## Features

- **Natural Language Task Management**: Add, list, complete, update, and delete tasks through conversation
- **Conversation History**: Chat history is persisted and retrievable across sessions
- **Shared Database**: Real-time sync with Phase 2 web dashboard
- **OpenAI-Powered**: Uses GPT-4o-mini for intelligent natural language understanding

## Architecture

```
todo-phase-3/
├── backend/           # Python FastAPI server
│   ├── app/
│   │   ├── main.py    # FastAPI application
│   │   ├── models/    # SQLModel data models
│   │   ├── mcp/       # MCP tools for task operations
│   │   ├── agent/     # OpenAI agent integration
│   │   └── api/       # REST API endpoints
│   └── tests/         # Pytest test suite
├── frontend/          # Next.js chat interface
│   └── src/
│       ├── app/       # Next.js app router
│       ├── components/ # React components
│       └── lib/       # API client utilities
└── specs/             # Feature specifications
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL database (shared with Phase 2)
- OpenAI API key

## Quick Start

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and OPENAI_API_KEY

# Run backend
uvicorn app.main:app --reload --port 8001
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API URL and user ID

# Run frontend
npm run dev
```

### 3. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/{user_id}/chat` | Send a chat message |

### Chat Request

```json
{
  "message": "Show me my tasks",
  "conversation_id": "optional-existing-conversation-id"
}
```

### Chat Response

```json
{
  "response": "Here are your tasks...",
  "conversation_id": "uuid"
}
```

## Example Interactions

- "Show me my tasks"
- "Add a task: Buy groceries"
- "Mark 'Buy groceries' as done"
- "Delete the task 'Buy groceries'"
- "What's on my todo list?"
- "Remind me to call mom"

## Testing

```bash
cd backend
pytest tests/ -v
```

## Environment Variables

### Backend (.env)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `OPENAI_API_KEY` | OpenAI API key |

### Frontend (.env.local)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend API URL |
| `NEXT_PUBLIC_USER_ID` | User ID for testing |
