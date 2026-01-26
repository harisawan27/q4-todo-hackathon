# Feature Specification: Todo AI Chatbot

**Feature Branch**: `001-todo-ai-chatbot`
**Created**: 2026-01-26
**Status**: Draft
**Input**: User description: "Phase 3: Todo AI Chatbot - Conversational Interface using OpenAI Agents SDK and MCP to manage Todo data via natural language"

## Overview

This feature adds a conversational AI interface (chatbot) to the existing Todo application. Users can manage their tasks through natural language instead of traditional UI interactions. The chatbot connects to the same Neon PostgreSQL database used in Phase 2, ensuring data consistency across both interfaces.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Chat to List Tasks (Priority: P1)

As a user, I want to ask the chatbot to show me my tasks so that I can quickly understand what I need to do without navigating through UI elements.

**Why this priority**: This is the most fundamental interaction - viewing existing data. Without this, the chatbot has no value. It validates the core architecture (database connection, agent integration, conversation flow).

**Independent Test**: Can be fully tested by sending "Show me my tasks" message and receiving a formatted list of the user's tasks from the shared database.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user with 3 tasks, **When** I type "Show me my tasks", **Then** the chatbot responds with a list of all 3 tasks showing title, description, and completion status.
2. **Given** I am an authenticated user with no tasks, **When** I type "What's on my todo list?", **Then** the chatbot responds that I have no tasks and offers to help me create one.
3. **Given** I am an authenticated user with 5 tasks (2 completed, 3 pending), **When** I type "Show me my pending tasks", **Then** the chatbot responds with only the 3 pending tasks.

---

### User Story 2 - Chat to Add Task (Priority: P1)

As a user, I want to add new tasks through natural language so that I can quickly capture ideas without filling out forms.

**Why this priority**: Task creation is core CRUD functionality and validates bidirectional data flow (write + read from shared DB).

**Independent Test**: Can be fully tested by sending "Add a task: Buy groceries" and verifying the task appears in both the chatbot list and the Phase 2 UI.

**Acceptance Scenarios**:

1. **Given** I am an authenticated user, **When** I type "Add a task: Buy groceries", **Then** the chatbot creates the task and confirms with "Task 'Buy groceries' has been added."
2. **Given** I am an authenticated user, **When** I type "Create a task called 'Review PR' with description 'Check the authentication changes'", **Then** the chatbot creates the task with both title and description.
3. **Given** I am an authenticated user, **When** I type "Remind me to call mom", **Then** the chatbot interprets this as adding a task titled "Call mom" and confirms creation.

---

### User Story 3 - Chat to Complete Task (Priority: P2)

As a user, I want to mark tasks as complete through conversation so that I can update my progress hands-free.

**Why this priority**: Completing tasks is essential for task management workflow, but depends on having tasks to complete (P1 stories).

**Independent Test**: Can be fully tested by sending "Mark 'Buy groceries' as done" and verifying the completion status updates in both interfaces.

**Acceptance Scenarios**:

1. **Given** I have a pending task titled "Buy groceries", **When** I type "Mark 'Buy groceries' as done", **Then** the chatbot marks the task complete and confirms.
2. **Given** I have multiple tasks with similar names, **When** I type "Complete the task about groceries", **Then** the chatbot identifies the matching task or asks for clarification if ambiguous.
3. **Given** I reference a task that doesn't exist, **When** I type "Complete 'Nonexistent task'", **Then** the chatbot responds that no matching task was found.

---

### User Story 4 - Chat to Update Task (Priority: P2)

As a user, I want to modify existing tasks through natural language so that I can refine task details without navigating forms.

**Why this priority**: Updates are important but less frequent than viewing/adding/completing tasks.

**Independent Test**: Can be fully tested by sending "Change the title of 'Buy groceries' to 'Buy organic groceries'" and verifying the update.

**Acceptance Scenarios**:

1. **Given** I have a task titled "Buy groceries", **When** I type "Change the title of 'Buy groceries' to 'Buy organic groceries'", **Then** the chatbot updates the title and confirms.
2. **Given** I have a task titled "Review PR", **When** I type "Add description 'Focus on error handling' to 'Review PR'", **Then** the chatbot updates the description and confirms.
3. **Given** I reference a task that doesn't exist, **When** I type "Update 'Nonexistent task'", **Then** the chatbot responds that no matching task was found.

---

### User Story 5 - Chat to Delete Task (Priority: P2)

As a user, I want to remove tasks through conversation so that I can clean up my task list efficiently.

**Why this priority**: Deletion is important for list hygiene but is a less frequent operation.

**Independent Test**: Can be fully tested by sending "Delete the task 'Buy groceries'" and verifying removal from both interfaces.

**Acceptance Scenarios**:

1. **Given** I have a task titled "Buy groceries", **When** I type "Delete the task 'Buy groceries'", **Then** the chatbot removes the task and confirms deletion.
2. **Given** I have a task titled "Important meeting", **When** I type "Remove 'Important meeting' from my list", **Then** the chatbot deletes the task and confirms.
3. **Given** I ask to delete a non-existent task, **When** I type "Delete 'Nonexistent task'", **Then** the chatbot responds that no matching task was found.

---

### User Story 6 - Conversation Persistence (Priority: P3)

As a user, I want my conversation history to be saved so that I can refer back to previous interactions.

**Why this priority**: Enhances user experience but is not critical for core task management functionality.

**Independent Test**: Can be fully tested by sending messages, refreshing the page, and verifying the conversation history is preserved.

**Acceptance Scenarios**:

1. **Given** I have an ongoing conversation, **When** I refresh the page, **Then** my previous messages and assistant responses are displayed.
2. **Given** I have no previous conversations, **When** I start the chatbot, **Then** I see an empty chat with a welcome message.
3. **Given** I have multiple conversations, **When** I return to the chatbot, **Then** I see my most recent conversation.

---

### Edge Cases

- What happens when the user sends an empty message? (System ignores or prompts for input)
- How does the system handle very long messages? (Truncate or reject with explanation)
- What happens when the database connection fails? (Show friendly error, allow retry)
- How does the system handle ambiguous task references? (Ask for clarification with matching options)
- What happens when the user's session expires mid-conversation? (Redirect to login, preserve message draft)
- How does the system handle requests for tasks belonging to other users? (Reject, only show user's own tasks)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST authenticate users before allowing chat interactions
- **FR-002**: System MUST connect to the existing Neon PostgreSQL database used by Phase 2
- **FR-003**: System MUST use the same Task data model as Phase 2 to ensure data compatibility
- **FR-004**: System MUST support adding tasks via natural language commands
- **FR-005**: System MUST support listing tasks with optional status filters (all, pending, completed)
- **FR-006**: System MUST support marking tasks as complete via natural language
- **FR-007**: System MUST support updating task title and description via natural language
- **FR-008**: System MUST support deleting tasks via natural language
- **FR-009**: System MUST persist conversation history (user messages and assistant responses)
- **FR-010**: System MUST retrieve conversation history when a user returns to continue chatting
- **FR-011**: System MUST scope all task operations to the authenticated user only
- **FR-012**: System MUST provide confirmation messages after successful task operations
- **FR-013**: System MUST handle unrecognized commands gracefully with helpful guidance
- **FR-014**: System MUST display task information in a human-readable format
- **FR-015**: System MUST be stateless on the backend - no in-memory state between requests

### Non-Functional Requirements

- **NFR-001**: Chat responses MUST be returned within 5 seconds under normal load
- **NFR-002**: System MUST support at least 100 concurrent chat sessions
- **NFR-003**: Conversation history MUST be retrievable within 1 second
- **NFR-004**: System MUST handle database connection failures gracefully with user-friendly messages

### Key Entities

- **Task**: Represents a todo item (inherited from Phase 2)
  - Attributes: user_id, id, title, description, completed, created_at, updated_at
  - Must mirror Phase 2 schema exactly for data compatibility

- **Conversation**: Represents a chat session
  - Attributes: user_id, id, created_at, updated_at
  - Relationship: belongs to User, has many Messages

- **Message**: Represents a single message in a conversation
  - Attributes: user_id, id, conversation_id, role (user/assistant), content, created_at
  - Relationship: belongs to Conversation

## Architecture Constraints

### Phase 2 Compatibility (Critical)

| Constraint | Requirement | Rationale |
|------------|-------------|-----------|
| **No Phase 2 Modifications** | Phase 2 codebase (`todo-phase-2/`) MUST NOT be modified in any way | Ensures Phase 2 remains stable and independently deployable |
| **Shared Database** | Phase 3 connects to the same Neon PostgreSQL database as Phase 2 | Enables real-time data synchronization between interfaces |
| **Task Schema Parity** | Phase 3 Task model MUST exactly match Phase 2's Task table schema | Data created in either interface must be readable by the other |
| **Independent Deployment** | Phase 3 must be deployable without affecting Phase 2 operation | Both systems can run simultaneously without conflicts |
| **Auth Compatibility** | Phase 3 uses the same Better Auth system and user identities | Users maintain single identity across both interfaces |

**Explicit Guarantees**:
- Tasks created via chatbot MUST appear immediately in Phase 2 UI
- Tasks created via Phase 2 UI MUST appear immediately in chatbot queries
- Task updates/deletes via either interface MUST be reflected in the other
- User authentication tokens from Phase 2 MUST work in Phase 3

### Core Architecture Decisions

1. **Monorepo Setup**: All Phase 3 code resides in `todo-phase-3` directory. Phase 2 code (`todo-phase-2`) MUST NOT be modified.

2. **Shared Database**: Phase 3 connects to the same Neon PostgreSQL database as Phase 2. The Task model definition must be replicated (not imported) to maintain codebase independence while ensuring schema compatibility.

3. **Stateless Backend**: The FastAPI server maintains no in-memory state. Each request:
   - Retrieves context from database
   - Processes via Agent/MCP
   - Saves results to database
   - Returns response

4. **MCP Integration**: The OpenAI Agents SDK connects to an MCP server that provides task management tools.

### Tech Stack (Fixed)

- **Frontend**: OpenAI ChatKit (Next.js/React)
- **Backend**: Python FastAPI + OpenAI Agents SDK
- **Integration**: Official MCP SDK (Python)
- **Database**: Neon Serverless PostgreSQL (SQLModel ORM)
- **Auth**: Better Auth

### MCP Server Tools

The MCP server MUST expose these tools to the agent:

| Tool | Parameters | Description |
|------|------------|-------------|
| `add_task` | user_id, title, description | Creates a new task |
| `list_tasks` | user_id, status (all/pending/completed) | Retrieves tasks with optional filter |
| `complete_task` | user_id, task_id | Marks a task as completed |
| `delete_task` | user_id, task_id | Removes a task permanently |
| `update_task` | user_id, task_id, title?, description? | Updates task fields |

### API Endpoint

- **POST** `/api/{user_id}/chat`
  - Request body: `{ "message": string, "conversation_id"?: string }`
  - Response: `{ "response": string, "conversation_id": string }`

### Agent Logic (Request Cycle)

**Endpoint**: POST `/api/{user_id}/chat`

| Step | Action | Description |
|------|--------|-------------|
| 1 | Fetch Conversation History | Retrieve all messages for the user's current conversation from the database to provide context |
| 2 | Append User Message | Store the incoming user message in the database before processing |
| 3 | Run OpenAI Agent | Execute the OpenAI Agent with MCP tools, passing conversation context. Agent interprets natural language and invokes appropriate MCP tools |
| 4 | Store Response & Tool Outputs | Persist the assistant's response and any tool execution results (task created, task list, etc.) to the database |
| 5 | Return Response | Send the formatted assistant response back to ChatKit for display |

**Request Flow Diagram**:
```
ChatKit → POST /api/{user_id}/chat → FastAPI Server
                                          ↓
                                    [1] Fetch history from DB
                                          ↓
                                    [2] Append user message to DB
                                          ↓
                                    [3] Run OpenAI Agent (MCP tools)
                                          ↓
                                    [4] Store response & tool outputs in DB
                                          ↓
                                    [5] Return response ← ChatKit
```

**Stateless Guarantee**: The backend maintains no in-memory state between requests. All context is reconstructed from the database on each request, ensuring horizontal scalability.

## Assumptions

- Users are already authenticated via Better Auth (same auth system as Phase 2)
- The Phase 2 Task table schema is stable and will not change
- OpenAI API keys are available and properly configured
- The Neon database connection string is shared via environment variables
- Users access the chatbot through a web interface

## Out of Scope

- Voice input/output
- Multi-language support (English only for Phase 3)
- Task sharing between users
- Recurring tasks
- Task due dates and reminders
- File attachments to tasks
- Integration with external calendars
- Mobile native app (web responsive is in scope)
- Modifications to Phase 2 codebase
- User registration (using existing users from Phase 2)

## Deliverables *(mandatory)*

### Directory Structure

```
todo-phase-3/
├── frontend/                    # OpenAI ChatKit Next.js application
│   ├── src/
│   │   ├── app/                 # Next.js app router pages
│   │   ├── components/          # React components for chat interface
│   │   └── lib/                 # Utilities and API client
│   ├── package.json
│   └── README.md
├── backend/                     # Python FastAPI server
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── models/              # SQLModel definitions (Task, Conversation, Message)
│   │   ├── mcp/                 # MCP server implementation and tools
│   │   ├── agent/               # OpenAI Agents SDK integration
│   │   └── api/                 # API route handlers
│   ├── requirements.txt
│   └── README.md
├── specs/                       # Specification files
│   └── 001-todo-ai-chatbot/
│       ├── spec.md              # This specification
│       ├── plan.md              # Implementation plan
│       └── tasks.md             # Task breakdown
└── README.md                    # Project README with setup instructions
```

### Deliverable Checklist

| Deliverable | Description | Acceptance |
|-------------|-------------|------------|
| `/frontend` directory | Fully functional ChatKit-based chat interface | Users can send messages and receive responses |
| `/backend` directory | FastAPI server with MCP integration | API responds to chat requests and executes MCP tools |
| MCP Server | Task management tools exposed via MCP protocol | All 5 tools (add, list, complete, update, delete) functional |
| Specification files | Complete specs in `/specs` directory | spec.md, plan.md, tasks.md present |
| Project README | Setup and run instructions | New developer can run the system in <10 minutes |

### Documentation Requirements

- **README.md** (root): Overview of Phase 3, prerequisites, quick start guide
- **backend/README.md**: Instructions for running the MCP server and FastAPI backend, environment variables, database setup
- **frontend/README.md**: Instructions for running ChatKit, API configuration, development setup

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create tasks via chat in under 10 seconds (from sending message to confirmation)
- **SC-002**: Users can view their task list via chat in under 5 seconds
- **SC-003**: Task operations performed via chatbot are immediately visible in Phase 2 UI (within 1 second)
- **SC-004**: 95% of natural language commands are correctly interpreted on first attempt
- **SC-005**: Conversation history is preserved across browser sessions
- **SC-006**: System handles 100 concurrent chat sessions without degradation
- **SC-007**: Users can perform all 5 core task operations (create, read, update, delete, complete) via natural language

### Definition of Done

- [ ] All P1 and P2 user stories pass acceptance scenarios
- [ ] Data created via chatbot appears correctly in Phase 2 UI
- [ ] Data created via Phase 2 UI appears correctly in chatbot queries
- [ ] Conversation history persists across page refreshes
- [ ] All MCP tools function correctly with proper error handling
- [ ] Authentication works correctly (users can only see/modify their own data)
- [ ] Edge cases are handled gracefully with helpful error messages
