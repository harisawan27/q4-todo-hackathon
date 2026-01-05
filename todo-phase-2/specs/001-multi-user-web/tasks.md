# Tasks: Phase II Multi-User Web Todo Application

**Input**: Design documents from `/specs/001-multi-user-web/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/openapi.yaml, research.md, quickstart.md

**Tests**: Tests are NOT explicitly requested in the specification. Test tasks are omitted. Add test tasks if TDD is desired.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/` and `frontend/` at repository root
- Backend: `backend/app/` for source, `backend/tests/` for tests
- Frontend: `frontend/app/` for pages, `frontend/lib/` for utilities, `frontend/components/` for UI

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create backend project structure with `backend/app/__init__.py`, `backend/app/main.py`, `backend/requirements.txt`
- [ ] T002 [P] Create frontend project structure: Initialize Next.js 16 app in `frontend/` with TypeScript
- [ ] T003 [P] Create `backend/.env.example` with DATABASE_URL, BETTER_AUTH_SECRET, HOST, PORT, DEBUG placeholders
- [ ] T004 [P] Create `frontend/.env.example` with BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL, BETTER_AUTH_URL placeholders
- [ ] T005 Configure backend linting with ruff, formatting with black, type checking with mypy in `backend/pyproject.toml`
- [ ] T006 [P] Configure frontend linting with ESLint, formatting with Prettier, Tailwind CSS in `frontend/`

**Checkpoint**: Project scaffolding complete - can run empty apps

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

### Database Infrastructure

- [ ] T007 Create database configuration in `backend/app/config.py` using pydantic-settings to load DATABASE_URL and BETTER_AUTH_SECRET from environment
- [ ] T008 Create SQLModel engine and session management in `backend/app/database.py` with `pool_pre_ping=True` for Neon connection handling
- [ ] T009 Create Task SQLModel in `backend/app/models/task.py` with id (UUID), user_id (FK, indexed), title (1-500 chars), completed (bool), created_at, updated_at
- [ ] T010 Create database initialization function in `backend/app/database.py` to create tables via SQLModel.metadata.create_all()

### Authentication Infrastructure (The Bridge)

- [ ] T011 Install python-jose[cryptography] and add to `backend/requirements.txt`
- [ ] T012 Create JWT verification dependency in `backend/app/auth/jwt_bearer.py` with HTTPBearer scheme extracting user_id from JWT `sub` claim using HS256 algorithm
- [ ] T013 Create `get_current_user` FastAPI dependency that returns user_id or raises HTTPException(401) for invalid/expired tokens

### FastAPI Application Core

- [ ] T014 Create FastAPI app instance in `backend/app/main.py` with CORS middleware allowing frontend origin (http://localhost:3000)
- [ ] T015 Create health check endpoint in `backend/app/routes/health.py` returning {"status": "healthy", "timestamp": datetime}
- [ ] T016 Register health route in `backend/app/main.py` (no auth required)

### Frontend Auth Infrastructure

- [ ] T017 Install better-auth, @tanstack/react-query in `frontend/package.json`
- [ ] T018 Create Better Auth server configuration in `frontend/lib/auth.ts` with JWT plugin using BETTER_AUTH_SECRET
- [ ] T019 Create Better Auth client configuration in `frontend/lib/auth-client.ts` with React hooks for session management
- [ ] T020 Create root layout in `frontend/app/layout.tsx` with QueryClientProvider and auth session provider
- [ ] T021 Create API client utility in `frontend/lib/api.ts` with automatic Authorization header injection from session token

### TypeScript Types

- [ ] T022 Create Task TypeScript types in `frontend/types/task.ts` matching TaskRead, TaskCreate, TaskUpdate schemas from OpenAPI contract

**Checkpoint**: Foundation ready - authentication bridge established, database connected, can verify JWT tokens

---

## Phase 3: User Story 1 - User Registration and Sign In (Priority: P1)

**Goal**: Users can sign up and sign in using Better Auth to access the application

**Independent Test**: Create account, sign out, sign back in - delivers secure access

### Implementation for User Story 1

- [ ] T023 [US1] Create auth layout in `frontend/app/(auth)/layout.tsx` with centered card styling
- [ ] T024 [P] [US1] Create sign-up page in `frontend/app/(auth)/sign-up/page.tsx` with email/password form using Better Auth signUp
- [ ] T025 [P] [US1] Create sign-in page in `frontend/app/(auth)/sign-in/page.tsx` with email/password form using Better Auth signIn
- [ ] T026 [US1] Create sign-up form component in `frontend/components/auth/sign-up-form.tsx` with validation (email format, password min length)
- [ ] T027 [US1] Create sign-in form component in `frontend/components/auth/sign-in-form.tsx` with error handling for invalid credentials
- [ ] T028 [US1] Create landing page in `frontend/app/page.tsx` that redirects authenticated users to /dashboard, unauthenticated to /sign-in
- [ ] T029 [US1] Create protected route wrapper in `frontend/lib/auth-client.ts` that redirects to /sign-in if no valid session
- [ ] T030 [US1] Add sign-out functionality to dashboard layout with Better Auth signOut call and redirect to /sign-in

**Checkpoint**: Users can register, sign in, sign out, and maintain session across browser refresh

---

## Phase 4: User Story 2 - Create and View Tasks (Priority: P1)

**Goal**: Authenticated users can create new tasks and view their task list

**Independent Test**: Create multiple tasks, verify they appear in list with correct details

### Backend Implementation for User Story 2

- [ ] T031 [US2] Create TaskCreate and TaskRead Pydantic schemas in `backend/app/models/task.py` for request/response validation
- [ ] T032 [US2] Create tasks router in `backend/app/routes/tasks.py` with APIRouter prefix="/api/tasks"
- [ ] T033 [US2] Implement POST /api/tasks endpoint in `backend/app/routes/tasks.py` with Depends(get_current_user), creating task with user_id from JWT
- [ ] T034 [US2] Implement GET /api/tasks endpoint in `backend/app/routes/tasks.py` returning all tasks WHERE user_id == current_user.user_id ordered by created_at DESC
- [ ] T035 [US2] Register tasks router in `backend/app/main.py`

### Frontend Implementation for User Story 2

- [ ] T036 [US2] Create dashboard layout in `frontend/app/dashboard/layout.tsx` with navigation header showing user email and sign-out button
- [ ] T037 [US2] Create dashboard page in `frontend/app/dashboard/page.tsx` with task list and create task form
- [ ] T038 [US2] Create task list component in `frontend/components/task-list.tsx` using React Query useQuery to fetch tasks from API
- [ ] T039 [US2] Create task item component in `frontend/components/task-item.tsx` displaying title and completion status
- [ ] T040 [US2] Create task form component in `frontend/components/task-form.tsx` with title input and submit button
- [ ] T041 [US2] Implement create task mutation in `frontend/components/task-form.tsx` using React Query useMutation with optimistic updates
- [ ] T042 [US2] Create empty state component in `frontend/components/empty-state.tsx` displayed when user has no tasks

**Checkpoint**: Users can create tasks and see them in their list immediately, persisting across page refresh

---

## Phase 5: User Story 3 - Complete and Uncomplete Tasks (Priority: P2)

**Goal**: Users can mark tasks as complete or incomplete to track progress

**Independent Test**: Toggle task completion multiple times, verify visual state updates and persists

### Backend Implementation for User Story 3

- [ ] T043 [US3] Implement POST /api/tasks/{taskId}/toggle endpoint in `backend/app/routes/tasks.py` flipping completed boolean, filtering by user_id
- [ ] T044 [US3] Add ownership check helper function in `backend/app/routes/tasks.py` that returns 404 for non-existent OR non-owned tasks

### Frontend Implementation for User Story 3

- [ ] T045 [US3] Add toggle checkbox/button to `frontend/components/task-item.tsx` with onClick handler
- [ ] T046 [US3] Implement toggle mutation in `frontend/components/task-item.tsx` using React Query useMutation calling POST /api/tasks/{id}/toggle
- [ ] T047 [US3] Add visual styling for completed tasks in `frontend/components/task-item.tsx` (strikethrough, muted color)

**Checkpoint**: Users can toggle task completion with immediate visual feedback and persistence

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can edit task titles to correct mistakes or update descriptions

**Independent Test**: Edit task title, verify change persists

### Backend Implementation for User Story 4

- [ ] T048 [US4] Create TaskUpdate Pydantic schema in `backend/app/models/task.py` with optional title and completed fields
- [ ] T049 [US4] Implement PUT /api/tasks/{taskId} endpoint in `backend/app/routes/tasks.py` for full replacement, filtering by user_id
- [ ] T050 [US4] Implement PATCH /api/tasks/{taskId} endpoint in `backend/app/routes/tasks.py` for partial updates, filtering by user_id

### Frontend Implementation for User Story 4

- [ ] T051 [US4] Add edit mode state to `frontend/components/task-item.tsx` with inline text input
- [ ] T052 [US4] Implement edit mutation in `frontend/components/task-item.tsx` using React Query useMutation calling PATCH /api/tasks/{id}
- [ ] T053 [US4] Add title validation in edit mode (non-empty, max 500 chars) with error display

**Checkpoint**: Users can edit task titles with validation and persistence

---

## Phase 7: User Story 5 - Delete Tasks (Priority: P2)

**Goal**: Users can delete tasks to keep their list clean and relevant

**Independent Test**: Delete task, verify it no longer appears in list

### Backend Implementation for User Story 5

- [ ] T054 [US5] Implement DELETE /api/tasks/{taskId} endpoint in `backend/app/routes/tasks.py` returning 204 on success, filtering by user_id

### Frontend Implementation for User Story 5

- [ ] T055 [US5] Add delete button to `frontend/components/task-item.tsx`
- [ ] T056 [US5] Create confirmation dialog component in `frontend/components/confirm-dialog.tsx` with cancel/confirm buttons
- [ ] T057 [US5] Implement delete mutation in `frontend/components/task-item.tsx` using React Query useMutation with confirmation flow

**Checkpoint**: Users can delete tasks with confirmation, task removed from list immediately

---

## Phase 8: User Story 6 - Data Isolation Between Users (Priority: P1)

**Goal**: Users cannot see or modify tasks belonging to other users

**Independent Test**: Create tasks as User A, sign in as User B, verify User A's tasks are not visible

### Implementation for User Story 6

- [ ] T058 [US6] Audit all task queries in `backend/app/routes/tasks.py` to ensure `.where(Task.user_id == current_user.user_id)` is present
- [ ] T059 [US6] Implement GET /api/tasks/{taskId} endpoint in `backend/app/routes/tasks.py` returning 404 for non-owned tasks (not 403, to prevent enumeration)
- [ ] T060 [US6] Add logging for access attempts in `backend/app/routes/tasks.py` to track potential unauthorized access patterns
- [ ] T061 [US6] Verify all mutation endpoints (POST, PUT, PATCH, DELETE) enforce user_id ownership check

**Checkpoint**: Complete user data isolation verified - users can only access their own tasks

---

## Phase 9: User Story 7 - Mobile-Responsive Dashboard (Priority: P2)

**Goal**: Users can access and manage tasks from any device

**Independent Test**: Access application on different viewport sizes, verify all functionality works

### Implementation for User Story 7

- [ ] T062 [US7] Configure Tailwind responsive breakpoints in `frontend/tailwind.config.ts` (sm: 640px, md: 768px, lg: 1024px)
- [ ] T063 [US7] Add responsive styles to `frontend/app/dashboard/layout.tsx` for mobile navigation (hamburger menu or simplified header)
- [ ] T064 [US7] Add responsive styles to `frontend/components/task-list.tsx` (full width on mobile, max-width on desktop)
- [ ] T065 [US7] Add responsive styles to `frontend/components/task-item.tsx` (touch-friendly tap targets, 44px minimum)
- [ ] T066 [US7] Add responsive styles to `frontend/components/task-form.tsx` (full width input on mobile)
- [ ] T067 [US7] Test and fix any horizontal scroll issues on viewports from 320px to 1920px

**Checkpoint**: Application fully functional on mobile, tablet, and desktop viewports

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T068 Add standardized error handling middleware in `backend/app/main.py` with Error schema (detail, code, status)
- [ ] T069 [P] Add loading states to all frontend components using React Query isLoading
- [ ] T070 [P] Add error states to all frontend components using React Query error with user-friendly messages
- [ ] T071 Add session expiration handling in `frontend/lib/auth-client.ts` with redirect to /sign-in and message
- [ ] T072 [P] Add favicon and meta tags to `frontend/app/layout.tsx`
- [ ] T073 Run accessibility audit (keyboard navigation, ARIA labels, color contrast)
- [ ] T074 Add environment variable validation on app startup in both `backend/app/main.py` and `frontend/` build
- [ ] T075 Run quickstart.md validation: verify all setup steps work end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (Auth) and US2 (Create/View) are both P1 and can proceed together once Foundation complete
  - US6 (Data Isolation) is P1 but naturally verified as US2 is implemented
  - US3, US4, US5, US7 are P2 and depend on US2 being complete (need tasks to exist)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Start After |
|-------|----------|--------------|-----------------|
| US1 (Auth) | P1 | Phase 2 | Foundational complete |
| US2 (Create/View) | P1 | Phase 2 + US1 frontend auth | US1 T029 complete |
| US6 (Isolation) | P1 | Phase 2 | Implemented alongside US2 |
| US3 (Toggle) | P2 | US2 | US2 complete |
| US4 (Edit) | P2 | US2 | US2 complete |
| US5 (Delete) | P2 | US2 | US2 complete |
| US7 (Responsive) | P2 | US2 | US2 complete |

### Within Each User Story

- Backend endpoints before frontend components that consume them
- Models/schemas before routes
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 Parallel Tasks**:
- T002, T003, T004, T005, T006 can run in parallel after T001

**Phase 2 Parallel Tasks**:
- T017-T022 (frontend foundation) can run in parallel with T007-T016 (backend foundation) once both T001 and T002 complete

**Phase 3 (US1) Parallel Tasks**:
- T024 and T025 (sign-up/sign-in pages) can run in parallel

**Phase 4 (US2) Parallel Tasks**:
- Backend tasks T031-T035 can complete before or in parallel with frontend setup
- Frontend tasks T038, T039, T040, T041, T042 can parallelize once T036-T037 complete

**Cross-Story Parallelism**:
- Once US2 is complete, US3, US4, US5, and US7 can all proceed in parallel (different files)

---

## Parallel Example: Phase 2 Foundation

```bash
# Launch backend foundation tasks together:
Task: "Create database configuration in backend/app/config.py"
Task: "Create SQLModel engine in backend/app/database.py"
Task: "Create Task SQLModel in backend/app/models/task.py"

# In parallel, launch frontend foundation:
Task: "Install better-auth, @tanstack/react-query"
Task: "Create Better Auth server configuration"
Task: "Create root layout with providers"
```

---

## Parallel Example: User Story 2

```bash
# Launch all backend API tasks together:
Task: "Create TaskCreate and TaskRead schemas"
Task: "Create tasks router with APIRouter"
Task: "Implement POST /api/tasks endpoint"
Task: "Implement GET /api/tasks endpoint"

# Then launch frontend components:
Task: "Create task list component"
Task: "Create task item component"
Task: "Create task form component"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 + 6)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. Complete Phase 4: User Story 2 (Create/View Tasks)
5. Complete Phase 8: User Story 6 (Data Isolation - audit only)
6. **STOP and VALIDATE**: Test auth flow and task CRUD independently
7. Deploy/demo MVP

### Incremental Delivery

| Increment | User Stories | Value Delivered |
|-----------|--------------|-----------------|
| MVP | US1 + US2 + US6 | Secure task creation and viewing |
| +Toggle | US3 | Track task completion |
| +Edit | US4 | Correct mistakes |
| +Delete | US5 | Clean up list |
| +Responsive | US7 | Mobile access |
| +Polish | All | Production-ready |

### Backend-First Strategy

Per plan.md, implement Backend-First:
1. Phases 1-2: Full foundation including backend API
2. Phase 4 backend tasks (T031-T035) before frontend
3. This ensures API is available for frontend integration
4. Health check (T15-T16) verifies backend is up before frontend work

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 75 |
| Phase 1 (Setup) | 6 tasks |
| Phase 2 (Foundational) | 16 tasks |
| Phase 3 (US1 - Auth) | 8 tasks |
| Phase 4 (US2 - Create/View) | 12 tasks |
| Phase 5 (US3 - Toggle) | 5 tasks |
| Phase 6 (US4 - Edit) | 6 tasks |
| Phase 7 (US5 - Delete) | 4 tasks |
| Phase 8 (US6 - Isolation) | 4 tasks |
| Phase 9 (US7 - Responsive) | 6 tasks |
| Phase 10 (Polish) | 8 tasks |
| Parallel Opportunities | 28 tasks marked [P] |
| MVP Scope | Phases 1-4 + Phase 8 (46 tasks) |

---

## Notes

- [P] tasks = different files, no dependencies on in-progress tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable after Foundation
- Backend-First: Complete API endpoints before frontend components
- Verify tests fail before implementing (if TDD approach adopted later)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Security-critical: Every query MUST filter by user_id
