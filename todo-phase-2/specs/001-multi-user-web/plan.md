# Implementation Plan: Phase II Multi-User Web Todo Application

**Branch**: `001-multi-user-web` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-multi-user-web/spec.md`

---

## Summary

Transform the Phase I CLI Todo application into a Phase II Multi-User Full-Stack Web Application with Next.js 16 frontend (Better Auth), FastAPI backend (SQLModel/python-jose), and Neon PostgreSQL database. The core requirement is 100% user data isolation enforced through JWT-based authentication where every API endpoint is protected and every database query filters by the authenticated user's ID.

**Strategy**: Backend-First implementation to ensure API availability before frontend integration.

---

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript (frontend)
**Primary Dependencies**: FastAPI, SQLModel, python-jose (backend); Next.js 16, Better-Auth, React Query (frontend)
**Storage**: Neon PostgreSQL with SQLModel ORM
**Testing**: pytest (backend), Jest/Vitest (frontend)
**Target Platform**: Web application (desktop, tablet, mobile responsive)
**Project Type**: Web (frontend + backend in monorepo)
**Performance Goals**: <2s response time for all CRUD operations, 100 concurrent users
**Constraints**: 100% user data isolation, JWT-based auth, shared secret synchronization
**Scale/Scope**: MVP with core task management; ~10 screens, single task list per user

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

### Pre-Design Verification

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Agentic Workflow | Spec exists before implementation | PASS |
| II. Core Stack | Technology choices match constitution | PASS |
| III. Reusable Intelligence | Skills/agents identified | PASS |
| IV. Security | JWT/user isolation requirements documented | PASS |
| V. Monorepo Navigation | Frontend/backend structure planned | PASS |
| VI. Iteration Goal | Phase II scope aligned with spec | PASS |

### Security Checklist (Per Constitution IV)

- [x] Every FastAPI endpoint requires `Depends(get_current_user)`
- [x] All SQLModel queries filter by `user_id` from JWT `sub` claim
- [x] `BETTER_AUTH_SECRET` synchronized between frontend/backend
- [x] No tokens in URL parameters (headers only)
- [x] Error responses sanitized (no sensitive data leakage)

### Skills/Agents Required

| Component | Skill/Agent | Reference |
|-----------|-------------|-----------|
| Auth Bridge | `better-auth-config` | `.claude/skills/better-auth-config/SKILL.md` |
| Security Review | `auth-architect` | `.claude/agents/auth-architect/AGENT.md` |
| Task CRUD | `create-task`, `update-task`, `delete-task`, `list-tasks`, `toggle-task` | `.claude/skills/` |
| Frontend Development | `frontend-dev` | `.claude/skills/frontend-dev/SKILL.md` |
| Backend Development | `backend-dev` | `.claude/skills/backend-dev/SKILL.md` |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-multi-user-web/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 research output
├── data-model.md        # Entity definitions
├── quickstart.md        # Developer setup guide
├── contracts/
│   └── openapi.yaml     # API contract
└── tasks.md             # Phase 2 output (via /sp.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Environment configuration
│   ├── database.py          # SQLModel engine and session
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_bearer.py    # JWT verification dependency
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # Task model and schemas
│   └── routes/
│       ├── __init__.py
│       ├── tasks.py         # Task CRUD endpoints
│       └── health.py        # Health check endpoint
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── test_tasks.py        # Task endpoint tests
│   └── test_auth.py         # Auth verification tests
├── .env.example
└── requirements.txt

frontend/
├── app/
│   ├── layout.tsx           # Root layout with providers
│   ├── page.tsx             # Landing page (redirect to dashboard or auth)
│   ├── (auth)/
│   │   ├── layout.tsx       # Auth layout
│   │   ├── sign-in/
│   │   │   └── page.tsx     # Sign in form
│   │   └── sign-up/
│   │       └── page.tsx     # Sign up form
│   └── dashboard/
│       ├── layout.tsx       # Dashboard layout with nav
│       └── page.tsx         # Task list view
├── lib/
│   ├── auth.ts              # Better Auth configuration
│   ├── auth-client.ts       # Client-side auth hooks
│   └── api.ts               # API client with auth headers
├── components/
│   ├── ui/                  # Reusable UI components
│   ├── task-list.tsx        # Task list component
│   ├── task-item.tsx        # Individual task component
│   ├── task-form.tsx        # Create/edit task form
│   └── auth/
│       ├── sign-in-form.tsx
│       └── sign-up-form.tsx
├── types/
│   └── task.ts              # TypeScript type definitions
├── .env.example
├── package.json
├── tsconfig.json
└── tailwind.config.ts
```

**Structure Decision**: Web application structure with `backend/` and `frontend/` at repository root, following Constitution V (Monorepo Navigation).

---

## Implementation Milestones

### Milestone 1: Database & Infrastructure

**Goal**: Establish database connection and core models.

**Deliverables**:
1. Configure Neon PostgreSQL connection in `backend/app/database.py`
2. Define Task model in `backend/app/models/task.py` with user_id foreign key
3. Create database initialization script
4. Verify connection with health check endpoint

**Security Gate**:
- No user data access until Milestone 2 (auth) is complete
- Health endpoint is the only public endpoint

---

### Milestone 2: Security & Middleware (The Bridge)

**Goal**: Implement JWT verification bridge between Better Auth and FastAPI.

**Deliverables**:
1. Implement `backend/app/auth/jwt_bearer.py` with:
   - `HTTPBearer` security scheme
   - `get_current_user` dependency extracting `user_id` from JWT `sub` claim
   - Proper error handling (401 for invalid/expired tokens)
2. Configure shared `BETTER_AUTH_SECRET` in environment
3. Create auth verification tests

**Skills Required**: `better-auth-config`
**Agent Activation**: `auth-architect` for security review

**Security Gate**:
- All subsequent endpoints MUST include `Depends(get_current_user)`
- JWT verification MUST use HS256 algorithm

---

### Milestone 3: Backend API Endpoints

**Goal**: Implement full Task CRUD API with user isolation.

**Deliverables**:
1. `GET /api/tasks` - List authenticated user's tasks
2. `POST /api/tasks` - Create task for authenticated user
3. `GET /api/tasks/{id}` - Get specific task (user-owned only)
4. `PUT /api/tasks/{id}` - Update task (user-owned only)
5. `PATCH /api/tasks/{id}` - Partial update (user-owned only)
6. `DELETE /api/tasks/{id}` - Delete task (user-owned only)
7. `POST /api/tasks/{id}/toggle` - Toggle completion status

**Skills Required**: `create-task`, `update-task`, `delete-task`, `list-tasks`, `toggle-task`

**Security Gate**:
- Every query MUST include `.where(Task.user_id == current_user.user_id)`
- 404 returned for non-existent OR non-owned resources (prevent enumeration)

---

### Milestone 4: Frontend Auth Integration

**Goal**: Set up Better Auth with Next.js and establish auth flow.

**Deliverables**:
1. Initialize Better Auth in `frontend/lib/auth.ts` with JWT plugin
2. Create sign-up and sign-in pages
3. Implement session management and token storage
4. Create protected route wrapper
5. Set up auth context for client components

**Skills Required**: `frontend-dev`

**Security Gate**:
- Token stored securely (httpOnly cookies or secure storage)
- Session refresh handled automatically

---

### Milestone 5: Frontend Task Management

**Goal**: Implement task UI with full CRUD operations.

**Deliverables**:
1. Task list component with empty state
2. Create task form with validation
3. Edit task functionality (inline or modal)
4. Delete task with confirmation
5. Toggle completion status
6. Responsive design for mobile/tablet/desktop

**Skills Required**: `frontend-dev`

**Dependencies**: Milestones 3 & 4 complete

---

### Milestone 6: Integration & Verification

**Goal**: End-to-end testing and security verification.

**Deliverables**:
1. Integration tests for auth flow
2. Cross-user isolation verification
3. Error handling verification
4. Performance verification (<2s response times)
5. Mobile responsiveness verification

**Agent Activation**: `auth-architect` for final security review

---

## Complexity Tracking

> No Constitution violations detected. This section is intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Design Artifacts Generated

| Artifact | Path | Description |
|----------|------|-------------|
| Research | `./research.md` | Technology decisions and alternatives |
| Data Model | `./data-model.md` | Entity definitions and relationships |
| API Contract | `./contracts/openapi.yaml` | OpenAPI 3.1 specification |
| Quickstart | `./quickstart.md` | Developer setup guide |

---

## Risk Analysis

### Top 3 Risks

| Risk | Mitigation | Blast Radius |
|------|------------|--------------|
| Secret mismatch between frontend/backend | Automated verification script, single source of truth | Auth completely broken |
| Cross-user data leakage | Query-level filtering mandatory, integration tests | Critical security incident |
| Session expiration during active use | Graceful redirect with message, token refresh flow | User frustration |

### Kill Switches

1. **Disable all endpoints**: Return 503 from health check if database unavailable
2. **Emergency secret rotation**: Documented procedure in operations runbook
3. **User lockout**: Ability to invalidate all sessions for a user

---

## ADR Candidates

The following architectural decisions may warrant formal ADRs:

1. **JWT vs Session-based Auth**: Decision to use JWT with shared secret for stateless auth
2. **Query-level vs RLS isolation**: Decision to use application-level user filtering

> Suggest: "Run `/sp.adr JWT Authentication Strategy` to document the auth decision"

---

## Next Steps

1. **Generate Tasks**: Run `/sp.tasks` to break milestones into actionable tasks
2. **Implement Backend First**: Start with Milestone 1 (Database & Infrastructure)
3. **Security Review**: Activate `auth-architect` agent for each milestone completion

---

## Post-Design Constitution Re-Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Agentic Workflow | PASS | Plan follows spec → plan → tasks flow |
| II. Core Stack | PASS | All technologies match constitution |
| III. Reusable Intelligence | PASS | Skills/agents mapped to milestones |
| IV. Security | PASS | Security gates at each milestone |
| V. Monorepo Navigation | PASS | frontend/ and backend/ structure defined |
| VI. Iteration Goal | PASS | All Phase II success criteria addressed |

**Constitution Gate**: PASSED - Proceeding to task generation.
