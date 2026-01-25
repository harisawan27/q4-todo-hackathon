<!--
## Sync Impact Report

**Version Change**: 1.0.0 → 1.1.0 (MINOR: Added Execution Protocol section)

**Modified Principles**: None

**Added Sections**:
- Execution Protocol (project initialization sequence)
- Expanded Architectural Flow with concrete example

**Removed Sections**: None

**Templates Requiring Updates**:
- ✅ `.specify/templates/plan-template.md` - Constitution Check section compatible
- ✅ `.specify/templates/spec-template.md` - Requirements section compatible
- ✅ `.specify/templates/tasks-template.md` - Task categories compatible

**Follow-up TODOs**: None
-->

# Todo AI Chatbot (Phase 3) Constitution

## Core Principles

### I. Data Compatibility First

Phase 3 shares the **same Neon PostgreSQL database** as Phase 2 (Web Dashboard). All SQLModel
definitions in Phase 3 MUST mirror Phase 2 exactly:

- Task model: `id`, `user_id`, `title`, `description`, `due_date`, `due_time`, `priority`, `tags`,
  `completed`, `created_at`, `updated_at`
- Notification model: `id`, `user_id`, `title`, `message`, `type`, `task_id`, `reminder_level`,
  `read`, `email_sent`, `created_at`

A task created via the Chatbot MUST appear immediately in the Web Dashboard and vice versa.

### II. Non-Destructive Schema Policy

Database schema changes are FORBIDDEN if they would break the existing Phase 2 application:

- No column removals or renames on shared tables (`tasks`, `notifications`, `push_subscriptions`)
- No type changes that alter existing data semantics
- New columns MUST have sensible defaults or be nullable
- Migration scripts MUST be backward-compatible

### III. Code Separation

While data is shared, code is NOT:

- Do NOT import modules from `todo-phase-2` into `todo-phase-3` (path resolution will fail)
- Replicate model definitions inside `todo-phase-3` to match Phase 2 exactly
- Each phase maintains its own dependencies, virtual environment, and deployment

### IV. MCP-First Architecture

The Model Context Protocol (MCP) Server is the "brain" of Phase 3:

- All CRUD operations on tasks MUST be implemented as MCP tools (`add_task`, `list_tasks`,
  `update_task`, `delete_task`, `complete_task`)
- The Agent calls MCP tools; it does NOT access the database directly
- MCP tools return structured responses; the Agent translates to natural language

### V. Stateless Agent Design

The OpenAI Agent MUST be stateless:

- No conversation memory persisted between requests
- Each request receives user input, calls MCP tools as needed, returns a response
- Session/user context passed explicitly via request parameters (e.g., `user_id`)
- No agent-side caching of database state

### VI. Enterprise-Grade Quality

System is designed for CEO-level workflows (Muhammad Haris Awan):

- All API endpoints MUST have proper error handling and validation
- Structured logging MUST be enabled for debugging and observability
- Secrets (database URLs, API keys) MUST use environment variables (`.env`), never hardcoded
- Response times for chatbot interactions SHOULD be under 2 seconds

## Integration & Compatibility Rules

1. **Shared Reality**: Both Phase 2 and Phase 3 connect to the same Neon PostgreSQL database
2. **Model Mirroring**: Phase 3 SQLModel classes MUST exactly match Phase 2 schema
3. **Read Before Write**: Always read `todo-phase-2/backend/app/models/` before defining Phase 3
   models
4. **Test Cross-Phase**: Verify that operations in Phase 3 reflect correctly in Phase 2 UI

## Technology Stack & Architecture

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | OpenAI ChatKit (Next.js)            |
| Backend    | Python FastAPI + OpenAI Agents SDK  |
| Brain      | MCP Server (Official SDK)           |
| Database   | Neon PostgreSQL (shared with Phase 2)|

### Architectural Flow

```
User Input → ChatKit Frontend → FastAPI Backend → OpenAI Agent → MCP Server → Neon DB
                                                       ↓
                                             Natural Language Response
```

**Concrete Example**:

```
User: "Add call with Asya to my list"
  → Agent receives input
  → Agent calls MCP tool: add_task(title="Call with Asya", user_id="...")
  → MCP Server creates row in shared DB
  → DB confirms insertion
  → Agent responds: "Added 'Call with Asya' to your tasks."
  → User opens Phase 2 Web Dashboard and sees the task
```

### Key Entities (from Phase 2)

- **Task**: Core todo item with title, description, due_date, due_time, priority, tags, completed
- **Notification**: System notifications for task events and reminders
- **PushSubscription**: Web push notification subscriptions (optional for Phase 3)

## Execution Protocol

The following sequence MUST be followed when initializing Phase 3 development:

### Step 1: Analyze Phase 2 Data Structure

Read and document the existing data models from `todo-phase-2/backend/app/models/`:

- `task.py` - Task, TaskCreate, TaskUpdate, TaskRead schemas
- `notification.py` - Notification schemas and reminder levels
- `push_subscription.py` - Push subscription schemas (if needed)

### Step 2: Create Phase 3 Folder Structure

```
todo-phase-3/
├── .specify/
│   └── memory/
│       └── constitution.md          # This file
├── specs/
│   ├── phase-3-requirements.md      # Feature specification
│   └── implementation_plan.md       # Architecture and implementation plan
├── backend/
│   ├── app/
│   │   ├── models/                  # Mirrored from Phase 2
│   │   ├── mcp/                     # MCP Server implementation
│   │   ├── agent/                   # OpenAI Agent implementation
│   │   └── api/                     # FastAPI endpoints
│   └── tests/
├── frontend/                        # ChatKit Next.js app
└── history/
    └── prompts/                     # PHR records
```

### Step 3: Generate Specification Documents

Create the following specification documents:

1. **`specs/phase-3-requirements.md`** - Feature requirements using `/sp.specify`
2. **`specs/implementation_plan.md`** - Architecture and task breakdown using `/sp.plan`

## Governance

1. **Constitution Supremacy**: This constitution supersedes all other development practices for
   Phase 3
2. **Amendment Process**: Changes require documentation, justification, and verification that Phase
   2 compatibility is maintained
3. **Compliance Review**: All PRs MUST verify adherence to Data Compatibility and Non-Destructive
   Schema policies
4. **Versioning**: Constitution follows semantic versioning (MAJOR.MINOR.PATCH)

**Version**: 1.1.0 | **Ratified**: 2026-01-25 | **Last Amended**: 2026-01-26
