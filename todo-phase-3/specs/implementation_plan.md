# Implementation Plan: Todo AI Chatbot (Phase 3)

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-01-26 | **Spec**: [specs/001-todo-ai-chatbot/spec.md](../specs/001-todo-ai-chatbot/spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

## Summary

Build a conversational AI chatbot that enables users to manage their todo tasks through natural language. The system uses:
- **OpenAI Agents SDK** for natural language understanding and conversation handling
- **MCP Server** (Official SDK) for task CRUD operations via 5 structured tools
- **Shared Neon PostgreSQL database** with Phase 2 for real-time data synchronization
- **OpenAI ChatKit** (Next.js) for the chat interface

---

## Technical Context

**Language/Version**: Python 3.11+ (Backend), TypeScript/Node.js (Frontend)
**Primary Dependencies**: FastAPI, OpenAI Agents SDK, Official MCP SDK, SQLModel, OpenAI ChatKit (Next.js)
**Storage**: Neon PostgreSQL (shared with Phase 2)
**Testing**: pytest (Backend), Vitest (Frontend)
**Target Platform**: Web application (responsive)
**Project Type**: Web (frontend + backend)
**Performance Goals**: <2 seconds chatbot response time, 100 concurrent sessions
**Constraints**: Stateless backend, shared database schema compatibility
**Scale/Scope**: Single user focus (authenticated user context)

---

## Constitution Check

*GATE: Must pass before implementation. Verified against `.specify/memory/constitution.md`*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Data Compatibility First | PASS | Task model will mirror Phase 2 exactly |
| II. Non-Destructive Schema Policy | PASS | Only adding new tables (Conversation, Message), no changes to existing |
| III. Code Separation | PASS | All code in `todo-phase-3/`, no imports from Phase 2 |
| IV. MCP-First Architecture | PASS | All CRUD via MCP tools (add_task, list_tasks, etc.) |
| V. Stateless Agent Design | PASS | No in-memory state, context from DB per request |
| VI. Enterprise-Grade Quality | PASS | Error handling, logging, env vars for secrets |

---

## Project Structure

### Documentation

```text
todo-phase-3/
├── specs/
│   └── implementation_plan.md    # This file
├── .specify/
│   └── memory/
│       └── constitution.md       # Project constitution
└── history/
    └── prompts/                  # PHR records
```

### Source Code

```text
todo-phase-3/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application entry
│   │   ├── config.py             # Settings and environment
│   │   ├── database.py           # SQLModel database connection
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── task.py           # Task model (mirrored from Phase 2)
│   │   │   ├── conversation.py   # Conversation model (new)
│   │   │   └── message.py        # Message model (new)
│   │   ├── mcp/
│   │   │   ├── __init__.py
│   │   │   ├── server.py         # MCP Server implementation
│   │   │   └── tools.py          # MCP tool definitions
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   └── runner.py         # OpenAI Agent runner
│   │   └── api/
│   │       ├── __init__.py
│   │       └── chat.py           # Chat endpoint
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_mcp_tools.py
│   │   ├── test_agent.py
│   │   └── test_api.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── page.tsx          # Main chat page
    │   │   └── layout.tsx
    │   ├── components/
    │   │   └── ChatInterface.tsx # ChatKit wrapper
    │   └── lib/
    │       └── api.ts            # API client
    ├── package.json
    └── .env.example
```

---

## Phase 2 Task Model Reference

**Source**: `todo-phase-2/backend/app/models/task.py`

The Task model from Phase 2 that MUST be replicated exactly:

```python
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = Field(default=None)
    due_time: Optional[time] = Field(default=None)
    priority: Optional[str] = Field(default=None, sa_column=Column(String(10)))
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

## Implementation Phases

> **AI Execution Note**: Each task below is designed to be executed by an AI agent without user intervention. Tasks are atomic and include explicit file paths, code patterns, and expected outputs.

### Task Summary

| Phase | Description | Task Count |
|-------|-------------|------------|
| **A** | Backend Core (Foundation) | 17 tasks |
| **B** | MCP Server (Brain) | 9 tasks |
| **C** | Agent Logic (Intelligence) | 13 tasks |
| **D** | Frontend (Interface) | 11 tasks |
| **V** | Cross-Phase Verification | 5 tasks |
| **Total** | | **55 tasks** |

---

### Phase A: Backend Core (Foundation)

**Objective**: Establish FastAPI server with database connection and replicated Task model.

- [ ] **A.1**: Read file `todo-phase-2/backend/app/models/task.py` and extract the complete `Task` class definition including all imports, fields, types, defaults, validators, and `__tablename__`. Document findings before proceeding.
  - **CRITICAL**: This MUST be the first task executed. Do not write any Phase 3 code until this analysis is complete.

- [ ] **A.2**: Create directory structure `todo-phase-3/backend/app/` with subdirectories: `models/`, `mcp/`, `agent/`, `api/`

- [ ] **A.3**: Create directory `todo-phase-3/backend/tests/`

- [ ] **A.4**: Create file `todo-phase-3/backend/app/__init__.py` with empty content

- [ ] **A.5**: Create file `todo-phase-3/backend/app/models/__init__.py` that exports `Task`, `Conversation`, `Message`

- [ ] **A.6**: Create file `todo-phase-3/backend/app/mcp/__init__.py` with empty content

- [ ] **A.7**: Create file `todo-phase-3/backend/app/agent/__init__.py` with empty content

- [ ] **A.8**: Create file `todo-phase-3/backend/app/api/__init__.py` with empty content

- [ ] **A.9**: Create file `todo-phase-3/backend/tests/__init__.py` with empty content

- [ ] **A.10**: Create file `todo-phase-3/backend/requirements.txt` with exact content:
  ```text
  fastapi>=0.109.0
  uvicorn[standard]>=0.27.0
  sqlmodel>=0.0.14
  python-dotenv>=1.0.0
  openai>=1.12.0
  mcp>=1.0.0
  psycopg2-binary>=2.9.9
  pytest>=8.0.0
  httpx>=0.26.0
  ```

- [ ] **A.11**: Create file `todo-phase-3/backend/.env.example` with content:
  ```text
  DATABASE_URL=postgresql://user:password@host:5432/dbname
  OPENAI_API_KEY=sk-your-openai-api-key
  ```

- [ ] **A.12**: Create file `todo-phase-3/backend/app/config.py` with Pydantic Settings class:
  - Import `pydantic_settings.BaseSettings`
  - Define `Settings` class with `DATABASE_URL: str` and `OPENAI_API_KEY: str`
  - Add `model_config` with `env_file = ".env"`
  - Export singleton `settings = Settings()`

- [ ] **A.13**: Create file `todo-phase-3/backend/app/database.py` with SQLModel engine:
  - Import `create_engine`, `Session` from `sqlmodel`
  - Import `settings` from `config`
  - Create `engine = create_engine(settings.DATABASE_URL)`
  - Define `get_session()` generator function that yields `Session(engine)`

- [ ] **A.14**: Create file `todo-phase-3/backend/app/models/task.py` with exact replica of Phase 2 Task model:
  - Copy all imports: `datetime`, `timezone`, `date`, `time`, `Optional`, `List`, `uuid4`, `Field`, `SQLModel`, `Column`, `JSON`, `String`
  - Copy `Priority` enum class exactly
  - Copy `Task` SQLModel class with `table=True` and `__tablename__ = "tasks"`
  - Include all 11 fields with exact types and defaults from Phase 2

- [ ] **A.15**: Create file `todo-phase-3/backend/app/models/conversation.py`:
  - Define `Conversation(SQLModel, table=True)` with `__tablename__ = "conversations"`
  - Fields: `id: str` (UUID primary key), `user_id: str` (indexed), `created_at: datetime`, `updated_at: datetime`

- [ ] **A.16**: Create file `todo-phase-3/backend/app/models/message.py`:
  - Define `MessageRole` enum with values `USER = "user"`, `ASSISTANT = "assistant"`
  - Define `Message(SQLModel, table=True)` with `__tablename__ = "messages"`
  - Fields: `id: str` (UUID primary key), `conversation_id: str` (indexed, foreign key), `user_id: str`, `role: str`, `content: str`, `created_at: datetime`

- [ ] **A.17**: Create file `todo-phase-3/backend/app/main.py`:
  - Import `FastAPI`, `CORSMiddleware`
  - Create `app = FastAPI(title="Todo AI Chatbot API")`
  - Add CORS middleware allowing all origins for development
  - Add `GET /health` endpoint returning `{"status": "healthy"}`
  - Add startup event to test database connection

#### Verification (Phase A)

```bash
# Install dependencies
cd todo-phase-3/backend
pip install -r requirements.txt

# Start the backend server
uvicorn app.main:app --reload --port 8001

# Test health endpoint (in another terminal)
curl http://localhost:8001/health

# Expected response:
# {"status": "healthy"}
```

---

### Phase B: MCP Server (Brain)

**Objective**: Implement the 5 MCP tools for task management using the Official MCP SDK.

**Tool Contract Reference**:
| Tool | Parameters | Returns |
|------|------------|---------|
| `add_task` | `user_id: str`, `title: str`, `description?: str` | `{"task_id": "...", "title": "...", "created": true}` |
| `list_tasks` | `user_id: str`, `status?: "all"\|"pending"\|"completed"` | `{"tasks": [...], "count": N}` |
| `complete_task` | `user_id: str`, `task_id: str` | `{"success": true, "task_id": "..."}` |
| `update_task` | `user_id: str`, `task_id: str`, `title?: str`, `description?: str` | `{"success": true, "task_id": "..."}` |
| `delete_task` | `user_id: str`, `task_id: str` | `{"success": true, "task_id": "..."}` |

- [ ] **B.1**: Create file `todo-phase-3/backend/app/mcp/server.py`:
  - Import `Server` from `mcp.server`
  - Import `stdio_server` from `mcp.server.stdio`
  - Create `mcp_server = Server("todo-mcp-server")`
  - Define `run_server()` async function using `stdio_server`

- [ ] **B.2**: Create file `todo-phase-3/backend/app/mcp/tools.py`:
  - Import `mcp_server` from `server`
  - Import `Tool` decorator from `mcp.server`
  - Import `Task` model and `get_session` from database

- [ ] **B.3**: In `app/mcp/tools.py`, implement `add_task` tool:
  - Decorator: `@mcp_server.tool()`
  - Function signature: `async def add_task(user_id: str, title: str, description: str = None) -> dict`
  - Create new `Task` instance with UUID, user_id, title, description
  - Insert into database using session
  - Return: `{"task_id": task.id, "title": task.title, "created": True}`

- [ ] **B.4**: In `app/mcp/tools.py`, implement `list_tasks` tool:
  - Decorator: `@mcp_server.tool()`
  - Function signature: `async def list_tasks(user_id: str, status: str = "all") -> dict`
  - Query tasks where `user_id` matches
  - Filter by `completed` field based on status parameter
  - Return: `{"tasks": [task.dict() for task in tasks], "count": len(tasks)}`

- [ ] **B.5**: In `app/mcp/tools.py`, implement `complete_task` tool:
  - Decorator: `@mcp_server.tool()`
  - Function signature: `async def complete_task(user_id: str, task_id: str) -> dict`
  - Query task by ID, verify user_id matches
  - Set `completed = True`, update `updated_at` to current UTC time
  - Return: `{"success": True, "task_id": task_id}`

- [ ] **B.6**: In `app/mcp/tools.py`, implement `update_task` tool:
  - Decorator: `@mcp_server.tool()`
  - Function signature: `async def update_task(user_id: str, task_id: str, title: str = None, description: str = None) -> dict`
  - Query task by ID, verify user_id matches
  - Update only provided fields (title and/or description)
  - Update `updated_at` to current UTC time
  - Return: `{"success": True, "task_id": task_id}`

- [ ] **B.7**: In `app/mcp/tools.py`, implement `delete_task` tool:
  - Decorator: `@mcp_server.tool()`
  - Function signature: `async def delete_task(user_id: str, task_id: str) -> dict`
  - Query task by ID, verify user_id matches
  - Delete from database
  - Return: `{"success": True, "task_id": task_id}`

- [ ] **B.8**: Add error handling to all MCP tools in `app/mcp/tools.py`:
  - Wrap each tool in try/except
  - Handle `TaskNotFoundError`: return `{"error": "Task not found", "code": "TASK_NOT_FOUND"}`
  - Handle `UnauthorizedError`: return `{"error": "Not authorized", "code": "UNAUTHORIZED"}`
  - Handle database errors: return `{"error": str(e), "code": "DB_ERROR"}`

- [ ] **B.9**: Create file `todo-phase-3/backend/tests/test_mcp_tools.py`:
  - Import `pytest`, all MCP tool functions
  - Create `@pytest.fixture` for test database session (use in-memory SQLite or mock)
  - Write `test_add_task()`: verify task is created with correct fields
  - Write `test_list_tasks_all()`: verify all tasks returned
  - Write `test_list_tasks_pending()`: verify only pending tasks returned
  - Write `test_list_tasks_completed()`: verify only completed tasks returned
  - Write `test_complete_task()`: verify task marked as completed
  - Write `test_update_task()`: verify task fields updated
  - Write `test_delete_task()`: verify task removed from database
  - Write `test_complete_task_not_found()`: verify error when task doesn't exist
  - Write `test_delete_task_wrong_user()`: verify error when user_id doesn't match

#### Verification (Phase B)

```bash
# Run MCP tool unit tests
cd todo-phase-3/backend
pytest tests/test_mcp_tools.py -v

# Expected output:
# test_add_task PASSED
# test_list_tasks_all PASSED
# test_list_tasks_pending PASSED
# test_list_tasks_completed PASSED
# test_complete_task PASSED
# test_update_task PASSED
# test_delete_task PASSED
# test_complete_task_not_found PASSED
# test_delete_task_wrong_user PASSED
```

---

### Phase C: Agent Logic (Intelligence)

**Objective**: Implement the OpenAI Agents SDK runner that processes natural language and calls MCP tools.

- [ ] **C.1**: Create file `todo-phase-3/backend/app/agent/runner.py`:
  - Import `Agent`, `Runner` from `openai_agents`
  - Import `settings` from `config`
  - Import MCP tools from `mcp.tools`
  - Initialize OpenAI client with `settings.OPENAI_API_KEY`

- [ ] **C.2**: In `app/agent/runner.py`, define system prompt constant:
  ```python
  SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural language conversation.

  Available actions:
  - Add tasks: "Add a task: <title>" or "Remind me to <task>"
  - List tasks: "Show my tasks" or "What's on my list?"
  - Complete tasks: "Mark <task> as done" or "Complete <task>"
  - Update tasks: "Change <task> to <new title>"
  - Delete tasks: "Delete <task>" or "Remove <task>"

  Always confirm successful operations with clear, friendly messages.
  If a task is ambiguous, ask for clarification.
  """
  ```

- [ ] **C.3**: In `app/agent/runner.py`, create `TodoAgent` class:
  - Constructor: accept `user_id: str`
  - Store `user_id` as instance variable
  - Create `Agent` instance with system prompt and MCP tools
  - Method: `async def run(self, message: str) -> str`

- [ ] **C.4**: In `app/agent/runner.py`, implement `get_conversation_history()` function:
  - Accept `conversation_id: str` parameter
  - Query `Message` table where `conversation_id` matches
  - Order by `created_at` ascending
  - Return list of `{"role": msg.role, "content": msg.content}`

- [ ] **C.5**: In `app/agent/runner.py`, implement `save_message()` function:
  - Accept `conversation_id: str`, `user_id: str`, `role: str`, `content: str`
  - Create new `Message` instance with UUID
  - Insert into database
  - Return `message.id`

- [ ] **C.6**: In `app/agent/runner.py`, implement `get_or_create_conversation()` function:
  - Accept `user_id: str`, `conversation_id: Optional[str]`
  - If `conversation_id` provided, query and return existing conversation
  - Otherwise, create new `Conversation` with UUID, return its ID

- [ ] **C.7**: In `app/agent/runner.py`, implement `run_agent()` function:
  - Signature: `async def run_agent(user_id: str, message: str, conversation_id: str = None) -> tuple[str, str]`
  - Step 1: Call `get_or_create_conversation(user_id, conversation_id)`
  - Step 2: Call `get_conversation_history(conversation_id)` to load context
  - Step 3: Call `save_message(conversation_id, user_id, "user", message)`
  - Step 4: Create `TodoAgent(user_id)` and call `agent.run(message)` with history context
  - Step 5: Call `save_message(conversation_id, user_id, "assistant", response)`
  - Step 6: Return `(response, conversation_id)`

- [ ] **C.8**: Create file `todo-phase-3/backend/app/api/chat.py`:
  - Import `APIRouter`, `HTTPException` from `fastapi`
  - Import `BaseModel` from `pydantic`
  - Import `run_agent` from `agent.runner`
  - Create `router = APIRouter()`

- [ ] **C.9**: In `app/api/chat.py`, define request/response models:
  ```python
  class ChatRequest(BaseModel):
      message: str
      conversation_id: Optional[str] = None

  class ChatResponse(BaseModel):
      response: str
      conversation_id: str
  ```

- [ ] **C.10**: In `app/api/chat.py`, implement chat endpoint:
  - Decorator: `@router.post("/api/{user_id}/chat", response_model=ChatResponse)`
  - Function: `async def chat(user_id: str, request: ChatRequest) -> ChatResponse`
  - Validate message is not empty
  - Call `run_agent(user_id, request.message, request.conversation_id)`
  - Return `ChatResponse(response=response, conversation_id=conv_id)`

- [ ] **C.11**: Update `app/main.py` to include chat router:
  - Import `router` from `api.chat`
  - Add `app.include_router(router)`

- [ ] **C.12**: Add structured logging in `app/agent/runner.py`:
  - Import `logging`
  - Create logger: `logger = logging.getLogger(__name__)`
  - Log at INFO level: agent start, tool calls, agent complete
  - Log at ERROR level: exceptions with stack trace

- [ ] **C.13**: Create file `todo-phase-3/backend/tests/test_api.py`:
  - Import `TestClient` from `fastapi.testclient`
  - Import `app` from `main`
  - Create `client = TestClient(app)`
  - Write `test_chat_add_task()`: POST message, verify response contains confirmation
  - Write `test_chat_list_tasks()`: POST message, verify response contains task list
  - Write `test_chat_empty_message()`: POST empty message, verify 400 error

#### Verification (Phase C)

```bash
# Ensure backend is running on port 8001
cd todo-phase-3/backend
uvicorn app.main:app --reload --port 8001

# Test 1: Add a task via chat
curl -X POST "http://localhost:8001/api/test-user-123/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task: Buy groceries"}'

# Expected response:
# {"response": "Task 'Buy groceries' has been added.", "conversation_id": "..."}

# Test 2: List tasks via chat (use same conversation_id from previous response)
curl -X POST "http://localhost:8001/api/test-user-123/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me my tasks", "conversation_id": "<id-from-step-1>"}'

# Expected response:
# {"response": "Here are your tasks:\n1. Buy groceries (pending)", "conversation_id": "..."}

# Test 3: Complete the task
curl -X POST "http://localhost:8001/api/test-user-123/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark Buy groceries as done"}'

# Expected response:
# {"response": "Task 'Buy groceries' has been marked as complete.", "conversation_id": "..."}

# Cross-check: Verify the task appears in Phase 2 UI at http://localhost:3000
```

---

### Phase D: Frontend (Interface)

**Objective**: Initialize and configure OpenAI ChatKit for the chat interface.

- [ ] **D.1**: Run command to initialize Next.js app:
  ```bash
  cd todo-phase-3
  npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --no-import-alias
  ```
  - Accept all defaults when prompted

- [ ] **D.2**: Install ChatKit and dependencies:
  ```bash
  cd todo-phase-3/frontend
  npm install @openai/chatkit
  ```

- [ ] **D.3**: Create file `todo-phase-3/frontend/.env.local`:
  ```text
  NEXT_PUBLIC_API_URL=http://localhost:8001
  NEXT_PUBLIC_USER_ID=demo-user-123
  ```

- [ ] **D.4**: Create file `todo-phase-3/frontend/.env.example`:
  ```text
  NEXT_PUBLIC_API_URL=http://localhost:8001
  NEXT_PUBLIC_USER_ID=your-user-id
  ```

- [ ] **D.5**: Create file `todo-phase-3/frontend/src/lib/api.ts`:
  - Define `API_URL` from `process.env.NEXT_PUBLIC_API_URL`
  - Define `USER_ID` from `process.env.NEXT_PUBLIC_USER_ID`
  - Export interface `ChatRequest { message: string; conversation_id?: string }`
  - Export interface `ChatResponse { response: string; conversation_id: string }`
  - Export async function `sendMessage(message: string, conversationId?: string): Promise<ChatResponse>`
  - Implement fetch POST to `${API_URL}/api/${USER_ID}/chat`
  - Handle errors and return typed response

- [ ] **D.6**: Create file `todo-phase-3/frontend/src/components/ChatInterface.tsx`:
  - Import `useState` from React
  - Import `sendMessage` from `lib/api`
  - Define component state: `messages: Array<{role: string, content: string}>`, `input: string`, `conversationId: string | null`, `isLoading: boolean`
  - Implement `handleSubmit` async function:
    - Add user message to messages array
    - Call `sendMessage(input, conversationId)`
    - Add assistant response to messages array
    - Update conversationId from response
  - Render chat UI with message list, input field, send button
  - Show loading indicator while waiting for response

- [ ] **D.7**: Update file `todo-phase-3/frontend/src/app/page.tsx`:
  - Import `ChatInterface` component
  - Render `<ChatInterface />` as main content
  - Add page title "Todo AI Chatbot"

- [ ] **D.8**: Update file `todo-phase-3/frontend/src/app/layout.tsx`:
  - Update metadata title to "Todo AI Chatbot"
  - Update metadata description

- [ ] **D.9**: Create file `todo-phase-3/frontend/src/app/globals.css` additions:
  - Add chat container styles (flex, height, overflow)
  - Add message bubble styles (user vs assistant)
  - Add input field styles
  - Add responsive breakpoints for mobile

- [ ] **D.10**: Update `todo-phase-3/frontend/next.config.js` if needed:
  - Add `rewrites` for API proxy (optional, for CORS in development)

- [ ] **D.11**: Create file `todo-phase-3/frontend/README.md`:
  - Document setup steps
  - Document environment variables
  - Document available scripts (dev, build, start)

#### Verification (Phase D)

```bash
# Terminal 1: Ensure backend is running
cd todo-phase-3/backend
uvicorn app.main:app --reload --port 8001

# Terminal 2: Start frontend
cd todo-phase-3/frontend
npm run dev

# Open http://localhost:3000 in browser

# Test 1: Type "Show me my tasks" and verify response appears
# Test 2: Type "Add task: Test from chatbot" and verify confirmation message
# Test 3: Type "Show me my tasks" again and verify new task appears in list
# Test 4: Open Phase 2 UI (http://localhost:3001) and verify the task appears there too
```

---

### Cross-Phase Verification (Final)

**Objective**: Verify end-to-end data synchronization between Phase 3 Chatbot and Phase 2 Web Dashboard.

- [ ] **V.1**: Create task via chatbot, verify in Phase 2:
  - Send message: "Add a task: Cross-phase test task"
  - Note the task title from response
  - Open Phase 2 UI at http://localhost:3001
  - Verify task "Cross-phase test task" appears in task list within 1 second

- [ ] **V.2**: Create task via Phase 2 UI, verify in chatbot:
  - Open Phase 2 UI and create task "Created from dashboard"
  - Switch to chatbot and send: "Show me my tasks"
  - Verify response includes "Created from dashboard"

- [ ] **V.3**: Complete task via chatbot, verify status in Phase 2:
  - Send message: "Mark 'Cross-phase test task' as done"
  - Verify chatbot confirms completion
  - Refresh Phase 2 UI
  - Verify task shows as completed (checkbox checked or struck through)

- [ ] **V.4**: Update task via chatbot, verify changes in Phase 2:
  - Send message: "Change 'Created from dashboard' to 'Updated via chatbot'"
  - Verify chatbot confirms update
  - Refresh Phase 2 UI
  - Verify task title changed to "Updated via chatbot"

- [ ] **V.5**: Delete task via chatbot, verify removal in Phase 2:
  - Send message: "Delete 'Updated via chatbot'"
  - Verify chatbot confirms deletion
  - Refresh Phase 2 UI
  - Verify task no longer appears in list

---

## MCP Tools Contract

| Tool | Parameters | Returns | Error Cases |
|------|------------|---------|-------------|
| `add_task` | `user_id: str`, `title: str`, `description?: str` | `{ task_id, title, created_at }` | Empty title |
| `list_tasks` | `user_id: str`, `status?: "all"\|"pending"\|"completed"` | `[{ id, title, completed, ... }]` | Invalid status |
| `complete_task` | `user_id: str`, `task_id: str` | `{ success: true, task_id }` | Task not found, wrong user |
| `update_task` | `user_id: str`, `task_id: str`, `title?: str`, `description?: str` | `{ success: true, task_id }` | Task not found, wrong user, no fields |
| `delete_task` | `user_id: str`, `task_id: str` | `{ success: true, task_id }` | Task not found, wrong user |

---

## API Contract

### POST `/api/{user_id}/chat`

**Request**:
```json
{
  "message": "string (required)",
  "conversation_id": "string (optional, omit for new conversation)"
}
```

**Response**:
```json
{
  "response": "string (assistant's natural language response)",
  "conversation_id": "string (use for subsequent messages)"
}
```

**Error Response**:
```json
{
  "error": "string (error message)",
  "code": "string (error code)"
}
```

---

## Dependencies

### Backend (`requirements.txt`)

```text
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlmodel>=0.0.14
python-dotenv>=1.0.0
openai>=1.12.0
mcp>=1.0.0
psycopg2-binary>=2.9.9
```

### Frontend (`package.json` dependencies)

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "@openai/chatkit": "latest"
  }
}
```

---

## Environment Variables

### Backend (`.env`)

```text
DATABASE_URL=postgresql://user:pass@host/dbname
OPENAI_API_KEY=sk-...
```

### Frontend (`.env.local`)

```text
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| Database schema mismatch with Phase 2 | Task A.1 mandates reading Phase 2 model before writing Phase 3 model |
| MCP SDK compatibility issues | Use official MCP SDK, test tools in isolation before Agent integration |
| OpenAI API rate limits | Implement retry logic with exponential backoff in agent runner |

---

## Success Criteria

- [ ] Task created via chatbot appears in Phase 2 UI within 1 second
- [ ] Task created via Phase 2 UI appears in chatbot query results
- [ ] All 5 MCP tools pass unit tests
- [ ] Chat endpoint returns response within 5 seconds
- [ ] Conversation history persists across page refreshes

---

## Next Steps

1. **Review and approve** this implementation plan
2. Run `/sp.tasks` to generate the detailed task breakdown with test cases
3. Begin **Phase A** implementation (Backend Core)
4. Validate each phase using the verification steps before proceeding to next phase

---

**Plan Generated**: 2026-01-26 | **Branch**: `001-todo-ai-chatbot`
