# Tasks: Todo AI Chatbot (Phase 3)

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)
**Branch**: `001-todo-ai-chatbot`
**Date**: 2026-01-26

**Tests**: Tests are included as the implementation plan specifies testing via pytest and manual verification steps.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (Phase 3)**: `backend/app/`, `frontend/src/`
- **Tests**: `backend/tests/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create directory structure and initialize project dependencies

- [x] T001 Read Phase 2 Task model from `todo-phase-2/backend/app/models/task.py` to extract schema for replication
- [x] T002 Create directory structure `todo-phase-3/backend/app/` with subdirectories: `models/`, `mcp/`, `agent/`, `api/`
- [x] T003 [P] Create directory `todo-phase-3/backend/tests/`
- [x] T004 [P] Create file `todo-phase-3/backend/app/__init__.py` with empty content
- [x] T005 [P] Create file `todo-phase-3/backend/app/models/__init__.py` that exports Task, Conversation, Message
- [x] T006 [P] Create file `todo-phase-3/backend/app/mcp/__init__.py` with empty content
- [x] T007 [P] Create file `todo-phase-3/backend/app/agent/__init__.py` with empty content
- [x] T008 [P] Create file `todo-phase-3/backend/app/api/__init__.py` with empty content
- [x] T009 [P] Create file `todo-phase-3/backend/tests/__init__.py` with empty content
- [x] T010 Create file `todo-phase-3/backend/requirements.txt` with dependencies: fastapi, uvicorn, sqlmodel, python-dotenv, openai, mcp, psycopg2-binary, pytest, httpx, pydantic-settings
- [x] T011 [P] Create file `todo-phase-3/backend/.env.example` with DATABASE_URL and OPENAI_API_KEY placeholders

**Checkpoint**: Directory structure ready for implementation ✓

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database & Configuration

- [x] T012 Create file `todo-phase-3/backend/app/config.py` with Pydantic Settings class (DATABASE_URL, OPENAI_API_KEY)
- [x] T013 Create file `todo-phase-3/backend/app/database.py` with SQLModel engine and get_session() generator

### Data Models (Replicated from Phase 2 + New)

- [x] T014 [P] Create file `todo-phase-3/backend/app/models/task.py` with exact replica of Phase 2 Task model (all 11 fields)
- [x] T015 [P] Create file `todo-phase-3/backend/app/models/conversation.py` with Conversation model (id, user_id, created_at, updated_at)
- [x] T016 [P] Create file `todo-phase-3/backend/app/models/message.py` with MessageRole enum and Message model (id, conversation_id, user_id, role, content, created_at)

### FastAPI Application Entry

- [x] T017 Create file `todo-phase-3/backend/app/main.py` with FastAPI app, CORS middleware, health endpoint, database startup test

### MCP Server Foundation

- [x] T018 Create file `todo-phase-3/backend/app/mcp/server.py` with MCP Server initialization using Official MCP SDK
- [x] T019 Create file `todo-phase-3/backend/app/mcp/tools.py` with MCP tool imports and server reference

### Verification

- [x] T020 Verify backend starts successfully with `uvicorn app.main:app --reload --port 8001`
- [x] T021 Verify health endpoint returns `{"status": "healthy"}` via GET http://localhost:8001/health

**Checkpoint**: Foundation ready - user story implementation can now begin ✓

---

## Phase 3: User Story 1 - Chat to List Tasks (Priority: P1)

**Goal**: Users can ask the chatbot to show their tasks via natural language

**Independent Test**: Send "Show me my tasks" message and receive a formatted list of tasks from the shared database

### MCP Tool Implementation for US1

- [x] T022 [US1] Implement `list_tasks` MCP tool in `backend/app/mcp/tools.py` with parameters: user_id, status (all/pending/completed)
- [x] T023 [US1] Add error handling to `list_tasks` tool for database errors and invalid status values

### Agent Implementation for US1

- [x] T024 [US1] Create file `todo-phase-3/backend/app/agent/runner.py` with imports and SYSTEM_PROMPT constant
- [x] T025 [US1] Implement `get_conversation_history()` function in `backend/app/agent/runner.py`
- [x] T026 [US1] Implement `save_message()` function in `backend/app/agent/runner.py`
- [x] T027 [US1] Implement `get_or_create_conversation()` function in `backend/app/agent/runner.py`
- [x] T028 [US1] Implement `TodoAgent` class in `backend/app/agent/runner.py` with OpenAI Agents SDK integration
- [x] T029 [US1] Implement `run_agent()` function in `backend/app/agent/runner.py` with 5-step request cycle

### API Endpoint for US1

- [x] T030 [US1] Create file `todo-phase-3/backend/app/api/chat.py` with APIRouter and ChatRequest/ChatResponse models
- [x] T031 [US1] Implement POST `/api/{user_id}/chat` endpoint in `backend/app/api/chat.py`
- [x] T032 [US1] Update `backend/app/main.py` to include chat router

### Tests for US1

- [x] T033 [P] [US1] Write `test_list_tasks_all()` in `backend/tests/test_mcp_tools.py`
- [x] T034 [P] [US1] Write `test_list_tasks_pending()` in `backend/tests/test_mcp_tools.py`
- [x] T035 [P] [US1] Write `test_list_tasks_completed()` in `backend/tests/test_mcp_tools.py`
- [ ] T036 [US1] Write `test_chat_list_tasks()` in `backend/tests/test_api.py`

### Verification for US1

- [ ] T037 [US1] Verify "Show me my tasks" returns formatted task list via POST `/api/{user_id}/chat`
- [ ] T038 [US1] Verify "Show me my pending tasks" returns only pending tasks
- [ ] T039 [US1] Verify empty task list returns helpful message offering to create tasks

**Checkpoint**: User Story 1 complete - users can list tasks via chat ✓

---

## Phase 4: User Story 2 - Chat to Add Task (Priority: P1)

**Goal**: Users can add new tasks through natural language commands

**Independent Test**: Send "Add a task: Buy groceries" and verify task appears in both chatbot list and Phase 2 UI

### MCP Tool Implementation for US2

- [x] T040 [US2] Implement `add_task` MCP tool in `backend/app/mcp/tools.py` with parameters: user_id, title, description (optional)
- [x] T041 [US2] Add error handling to `add_task` tool for empty title and database errors

### Tests for US2

- [x] T042 [P] [US2] Write `test_add_task()` in `backend/tests/test_mcp_tools.py`
- [x] T043 [P] [US2] Write `test_add_task_with_description()` in `backend/tests/test_mcp_tools.py`
- [ ] T044 [US2] Write `test_chat_add_task()` in `backend/tests/test_api.py`

### Verification for US2

- [ ] T045 [US2] Verify "Add a task: Buy groceries" creates task and returns confirmation
- [ ] T046 [US2] Verify "Remind me to call mom" creates task titled "Call mom"
- [ ] T047 [US2] Verify task created via chatbot appears in Phase 2 UI within 1 second

**Checkpoint**: User Story 2 complete - users can add tasks via chat ✓

---

## Phase 5: User Story 3 - Chat to Complete Task (Priority: P2)

**Goal**: Users can mark tasks as complete through conversation

**Independent Test**: Send "Mark 'Buy groceries' as done" and verify completion status updates in both interfaces

### MCP Tool Implementation for US3

- [x] T048 [US3] Implement `complete_task` MCP tool in `backend/app/mcp/tools.py` with parameters: user_id, task_id
- [x] T049 [US3] Add error handling for task not found and unauthorized access in `complete_task`

### Tests for US3

- [x] T050 [P] [US3] Write `test_complete_task()` in `backend/tests/test_mcp_tools.py`
- [x] T051 [P] [US3] Write `test_complete_task_not_found()` in `backend/tests/test_mcp_tools.py`
- [ ] T052 [US3] Write `test_chat_complete_task()` in `backend/tests/test_api.py`

### Verification for US3

- [ ] T053 [US3] Verify "Mark 'Buy groceries' as done" marks task complete and confirms
- [ ] T054 [US3] Verify ambiguous task reference asks for clarification
- [ ] T055 [US3] Verify non-existent task returns "no matching task found" message

**Checkpoint**: User Story 3 complete - users can complete tasks via chat ✓

---

## Phase 6: User Story 4 - Chat to Update Task (Priority: P2)

**Goal**: Users can modify existing tasks through natural language

**Independent Test**: Send "Change the title of 'Buy groceries' to 'Buy organic groceries'" and verify the update

### MCP Tool Implementation for US4

- [x] T056 [US4] Implement `update_task` MCP tool in `backend/app/mcp/tools.py` with parameters: user_id, task_id, title (optional), description (optional)
- [x] T057 [US4] Add error handling for task not found, unauthorized access, and no fields provided in `update_task`

### Tests for US4

- [x] T058 [P] [US4] Write `test_update_task_title()` in `backend/tests/test_mcp_tools.py`
- [x] T059 [P] [US4] Write `test_update_task_description()` in `backend/tests/test_mcp_tools.py`
- [x] T060 [P] [US4] Write `test_update_task_not_found()` in `backend/tests/test_mcp_tools.py`
- [ ] T061 [US4] Write `test_chat_update_task()` in `backend/tests/test_api.py`

### Verification for US4

- [ ] T062 [US4] Verify "Change the title of 'Buy groceries' to 'Buy organic groceries'" updates title
- [ ] T063 [US4] Verify "Add description 'Focus on error handling' to 'Review PR'" updates description
- [ ] T064 [US4] Verify non-existent task returns "no matching task found" message

**Checkpoint**: User Story 4 complete - users can update tasks via chat ✓

---

## Phase 7: User Story 5 - Chat to Delete Task (Priority: P2)

**Goal**: Users can remove tasks through conversation

**Independent Test**: Send "Delete the task 'Buy groceries'" and verify removal from both interfaces

### MCP Tool Implementation for US5

- [x] T065 [US5] Implement `delete_task` MCP tool in `backend/app/mcp/tools.py` with parameters: user_id, task_id
- [x] T066 [US5] Add error handling for task not found and unauthorized access in `delete_task`

### Tests for US5

- [x] T067 [P] [US5] Write `test_delete_task()` in `backend/tests/test_mcp_tools.py`
- [x] T068 [P] [US5] Write `test_delete_task_not_found()` in `backend/tests/test_mcp_tools.py`
- [x] T069 [P] [US5] Write `test_delete_task_wrong_user()` in `backend/tests/test_mcp_tools.py`
- [ ] T070 [US5] Write `test_chat_delete_task()` in `backend/tests/test_api.py`

### Verification for US5

- [ ] T071 [US5] Verify "Delete the task 'Buy groceries'" removes task and confirms
- [ ] T072 [US5] Verify "Remove 'Important meeting' from my list" deletes task
- [ ] T073 [US5] Verify non-existent task returns "no matching task found" message

**Checkpoint**: User Story 5 complete - users can delete tasks via chat ✓

---

## Phase 8: User Story 6 - Conversation Persistence (Priority: P3)

**Goal**: Conversation history is saved and retrievable across sessions

**Independent Test**: Send messages, refresh the page, verify conversation history is preserved

### Implementation for US6

- [x] T074 [US6] Verify Conversation model creates and retrieves conversations correctly
- [x] T075 [US6] Verify Message model stores and retrieves messages with correct ordering
- [x] T076 [US6] Add logging for conversation operations in `backend/app/agent/runner.py`

### Tests for US6

- [ ] T077 [P] [US6] Write `test_conversation_create()` in `backend/tests/test_api.py`
- [ ] T078 [P] [US6] Write `test_conversation_history_retrieval()` in `backend/tests/test_api.py`
- [ ] T079 [US6] Write `test_chat_preserves_conversation_id()` in `backend/tests/test_api.py`

### Verification for US6

- [ ] T080 [US6] Verify conversation history persists across multiple requests with same conversation_id
- [ ] T081 [US6] Verify new conversation starts with welcome context when no conversation_id provided
- [ ] T082 [US6] Verify most recent conversation loads when user returns

**Checkpoint**: User Story 6 complete - conversation history persists ✓

---

## Phase 9: Frontend (Chat Interface)

**Purpose**: Initialize and configure OpenAI ChatKit for the chat interface

### Project Initialization

- [x] T083 Initialize Next.js app in `todo-phase-3/frontend/` with TypeScript, Tailwind, ESLint, App Router
- [x] T084 Install ChatKit dependency: `npm install @openai/chatkit`
- [x] T085 [P] Create file `todo-phase-3/frontend/.env.local` with NEXT_PUBLIC_API_URL and NEXT_PUBLIC_USER_ID
- [x] T086 [P] Create file `todo-phase-3/frontend/.env.example` with environment variable placeholders

### API Client

- [x] T087 Create file `todo-phase-3/frontend/src/lib/api.ts` with ChatRequest/ChatResponse interfaces and sendMessage function

### Chat Components

- [x] T088 Create file `todo-phase-3/frontend/src/components/ChatInterface.tsx` with chat UI, message list, input field, loading state
- [x] T089 Update file `todo-phase-3/frontend/src/app/page.tsx` to render ChatInterface component
- [x] T090 Update file `todo-phase-3/frontend/src/app/layout.tsx` with metadata title "Todo AI Chatbot"
- [x] T091 Update file `todo-phase-3/frontend/src/app/globals.css` with chat container and message bubble styles

### Configuration

- [x] T092 [P] Update `todo-phase-3/frontend/next.config.js` with API proxy rewrites if needed
- [x] T093 [P] Create file `todo-phase-3/frontend/README.md` with setup steps and environment variables

### Verification

- [ ] T094 Verify frontend starts successfully with `npm run dev` on port 3000
- [ ] T095 Verify chat interface renders with message input and send button
- [ ] T096 Verify sending "Show me my tasks" returns response from backend

**Checkpoint**: Frontend complete - chat interface functional ✓

---

## Phase 10: Cross-Phase Verification (End-to-End)

**Purpose**: Verify data synchronization between Phase 3 Chatbot and Phase 2 Web Dashboard

- [ ] T097 Verify task created via chatbot ("Add task: Cross-phase test") appears in Phase 2 UI within 1 second
- [ ] T098 Verify task created via Phase 2 UI appears in chatbot query results ("Show my tasks")
- [ ] T099 Verify task completed via chatbot shows as completed in Phase 2 UI
- [ ] T100 Verify task updated via chatbot reflects changes in Phase 2 UI
- [ ] T101 Verify task deleted via chatbot is removed from Phase 2 UI

**Checkpoint**: Full bidirectional data sync confirmed

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, error handling, and final improvements

- [x] T102 [P] Create file `todo-phase-3/README.md` with project overview, prerequisites, and quick start guide
- [x] T103 [P] Create file `todo-phase-3/backend/README.md` with backend setup, environment variables, and run instructions
- [x] T104 Add structured logging across all agent operations in `backend/app/agent/runner.py`
- [x] T105 Add edge case handling: empty messages, long messages, database connection failures
- [x] T106 [P] Write `test_chat_empty_message()` in `backend/tests/test_api.py` (verify 400 error)
- [ ] T107 Run all pytest tests and verify all pass: `pytest backend/tests/ -v`
- [ ] T108 Verify response time under 5 seconds for typical chat operations

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories
- **Phase 3-8 (User Stories)**: All depend on Phase 2 completion
  - US1 (P1) and US2 (P1) can proceed in parallel after Phase 2
  - US3-5 (P2) can proceed in parallel after US1/US2 or concurrently
  - US6 (P3) depends on conversation infrastructure from US1
- **Phase 9 (Frontend)**: Depends on Phase 3 (US1) minimum for testing
- **Phase 10 (Verification)**: Depends on all user stories + frontend
- **Phase 11 (Polish)**: Depends on all verification complete

### User Story Dependencies

| Story | Priority | Can Start After | Dependencies |
|-------|----------|-----------------|--------------|
| US1 - List Tasks | P1 | Phase 2 | None |
| US2 - Add Task | P1 | Phase 2 | None (shares agent infra with US1) |
| US3 - Complete Task | P2 | Phase 2 | None (needs tasks to exist) |
| US4 - Update Task | P2 | Phase 2 | None (needs tasks to exist) |
| US5 - Delete Task | P2 | Phase 2 | None (needs tasks to exist) |
| US6 - Conversation | P3 | Phase 2 | US1 (agent infrastructure) |

### Parallel Opportunities

- **Within Phase 1**: T003-T009, T011 can run in parallel
- **Within Phase 2**: T014-T016 (models) can run in parallel
- **Across User Stories**: US1 and US2 can run in parallel; US3, US4, US5 can run in parallel
- **Tests**: All tests marked [P] within a phase can run in parallel

---

## Parallel Execution Examples

### Example 1: Phase 2 Model Creation

```bash
# Launch all model tasks in parallel:
Task T014: "Create Task model in backend/app/models/task.py"
Task T015: "Create Conversation model in backend/app/models/conversation.py"
Task T016: "Create Message model in backend/app/models/message.py"
```

### Example 2: User Story 3-5 Implementation (P2 stories)

```bash
# After Phase 2 complete, launch P2 stories in parallel:
Task T048-T055: "User Story 3 - Complete Task"
Task T056-T064: "User Story 4 - Update Task"
Task T065-T073: "User Story 5 - Delete Task"
```

### Example 3: MCP Tool Tests

```bash
# Launch all MCP tool tests in parallel:
Task T033: "test_list_tasks_all()"
Task T034: "test_list_tasks_pending()"
Task T035: "test_list_tasks_completed()"
Task T042: "test_add_task()"
Task T050: "test_complete_task()"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (List Tasks)
4. Complete Phase 4: User Story 2 (Add Tasks)
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready - users can view and add tasks

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US2 → Test independently → Deploy (MVP!)
3. Add US3-5 → Test independently → Deploy (Full CRUD!)
4. Add US6 → Test independently → Deploy (Conversations!)
5. Add Frontend → Test independently → Deploy (Full UI!)
6. Each story adds value without breaking previous stories

### Suggested MVP Scope

- **Minimum Viable Product**: Phase 1 + Phase 2 + Phase 3 (US1) + Phase 4 (US2)
- **Why**: Users can view tasks and add tasks - core value proposition delivered
- **Effort**: ~30 tasks to functional MVP

---

## Summary

| Phase | Description | Task Count | Parallelizable |
|-------|-------------|------------|----------------|
| 1 | Setup | 11 | 8 |
| 2 | Foundational | 10 | 3 |
| 3 | US1 - List Tasks (P1) | 18 | 4 |
| 4 | US2 - Add Task (P1) | 8 | 3 |
| 5 | US3 - Complete Task (P2) | 8 | 3 |
| 6 | US4 - Update Task (P2) | 9 | 4 |
| 7 | US5 - Delete Task (P2) | 9 | 4 |
| 8 | US6 - Conversation (P3) | 9 | 3 |
| 9 | Frontend | 14 | 4 |
| 10 | Cross-Phase Verification | 5 | 0 |
| 11 | Polish | 7 | 3 |
| **Total** | | **108** | **39** |

---

## Notes

- [P] tasks = different files, no dependencies - can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All task IDs follow strict format: `- [ ] T### [P?] [US#?] Description with file path`
