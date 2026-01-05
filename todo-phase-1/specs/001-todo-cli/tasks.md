# Tasks: Todo In-Memory Python Console App

**Input**: Design documents from `/specs/001-todo-cli/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), data-model.md, quickstart.md

**Tests**: Included - spec implies comprehensive testing per Constitution VIII (Code Quality Standards)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root (per plan.md)
- Domain layer: `src/models.py`
- Service layer: `src/manager.py`
- CLI layer: `src/main.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization with uv and basic structure

- [X] T001 Initialize uv project with `uv init` and configure pyproject.toml for Python 3.13+
- [X] T002 [P] Create src/ directory with `src/__init__.py` package marker
- [X] T003 [P] Create tests/ directory with `tests/__init__.py` package marker
- [X] T004 Add dev dependencies: `uv add --dev pytest pytest-cov`
- [X] T005 Verify setup: `uv run python -c "import src"` succeeds

**Checkpoint**: Project structure ready, imports working

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain models and exceptions that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create Task dataclass with fields (id, title, description, completed) in src/models.py
- [X] T007 [P] Create TaskNotFoundError exception class in src/models.py
- [X] T008 [P] Create ValidationError exception class in src/models.py
- [X] T009 Create TaskManager class skeleton with `_tasks: dict[int, Task]` and `_next_id: int` in src/manager.py
- [X] T010 [P] Create unit tests for Task dataclass in tests/test_models.py
- [X] T011 [P] Create unit tests for exception classes in tests/test_models.py
- [X] T012 Run tests: `uv run pytest tests/test_models.py -v`

**Checkpoint**: Foundation ready - Task entity and exceptions work, tests pass

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1) - MVP

**Goal**: Users can create tasks with title and description, stored in memory with unique sequential ID

**Independent Test**: Run app, select "Add Task", enter title/description, verify task created with ID 1

### Tests for User Story 1

- [X] T013 [P] [US1] Write unit test for `TaskManager.add()` with valid input in tests/test_manager.py
- [X] T014 [P] [US1] Write unit test for `TaskManager.add()` with empty title (ValidationError) in tests/test_manager.py
- [X] T015 [P] [US1] Write unit test for `TaskManager.add()` with title at boundary (500 chars) in tests/test_manager.py
- [X] T016 [US1] Run US1 tests and verify they FAIL: `uv run pytest tests/test_manager.py -k "add" -v`

### Implementation for User Story 1

- [X] T017 [US1] Implement title validation method `validate_title(title: str) -> str` in src/models.py
- [X] T018 [US1] Implement description validation method `validate_description(desc: str) -> str` in src/models.py
- [X] T019 [US1] Implement `TaskManager.add(title: str, description: str = "") -> Task` in src/manager.py
- [X] T020 [US1] Run US1 tests and verify they PASS: `uv run pytest tests/test_manager.py -k "add" -v`

**Checkpoint**: User Story 1 complete - can add tasks programmatically, all acceptance scenarios covered

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1) - MVP

**Goal**: Users can see all tasks with ID, status indicator, title, and description

**Independent Test**: Add multiple tasks, call get_all(), verify all appear with correct formatting

### Tests for User Story 2

- [X] T021 [P] [US2] Write unit test for `TaskManager.get_all()` with multiple tasks in tests/test_manager.py
- [X] T022 [P] [US2] Write unit test for `TaskManager.get_all()` with no tasks (empty list) in tests/test_manager.py
- [X] T023 [P] [US2] Write unit test for `TaskManager.get(task_id)` with valid ID in tests/test_manager.py
- [X] T024 [P] [US2] Write unit test for `TaskManager.get(task_id)` with invalid ID (TaskNotFoundError) in tests/test_manager.py
- [X] T025 [US2] Run US2 tests and verify they FAIL: `uv run pytest tests/test_manager.py -k "get" -v`

### Implementation for User Story 2

- [X] T026 [US2] Implement `TaskManager.get(task_id: int) -> Task` in src/manager.py
- [X] T027 [US2] Implement `TaskManager.get_all() -> list[Task]` in src/manager.py
- [X] T028 [US2] Run US2 tests and verify they PASS: `uv run pytest tests/test_manager.py -k "get" -v`

**Checkpoint**: User Story 2 complete - can view tasks programmatically, all acceptance scenarios covered

---

## Phase 5: User Story 3 - Toggle Task Completion (Priority: P2)

**Goal**: Users can mark tasks complete/incomplete by toggling the completed status

**Independent Test**: Create task (incomplete), toggle (becomes complete), toggle again (becomes incomplete)

### Tests for User Story 3

- [X] T029 [P] [US3] Write unit test for `TaskManager.toggle()` incomplete to complete in tests/test_manager.py
- [X] T030 [P] [US3] Write unit test for `TaskManager.toggle()` complete to incomplete in tests/test_manager.py
- [X] T031 [P] [US3] Write unit test for `TaskManager.toggle()` with invalid ID (TaskNotFoundError) in tests/test_manager.py
- [X] T032 [US3] Run US3 tests and verify they FAIL: `uv run pytest tests/test_manager.py -k "toggle" -v`

### Implementation for User Story 3

- [X] T033 [US3] Implement `TaskManager.toggle(task_id: int) -> Task` in src/manager.py
- [X] T034 [US3] Run US3 tests and verify they PASS: `uv run pytest tests/test_manager.py -k "toggle" -v`

**Checkpoint**: User Story 3 complete - can toggle task completion programmatically

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Users can modify title and/or description of existing tasks

**Independent Test**: Create task, update title only (description unchanged), update description only (title unchanged), update both

### Tests for User Story 4

- [X] T035 [P] [US4] Write unit test for `TaskManager.update()` title only in tests/test_manager.py
- [X] T036 [P] [US4] Write unit test for `TaskManager.update()` description only in tests/test_manager.py
- [X] T037 [P] [US4] Write unit test for `TaskManager.update()` both fields in tests/test_manager.py
- [X] T038 [P] [US4] Write unit test for `TaskManager.update()` with invalid ID (TaskNotFoundError) in tests/test_manager.py
- [X] T039 [P] [US4] Write unit test for `TaskManager.update()` with invalid title (ValidationError) in tests/test_manager.py
- [X] T040 [US4] Run US4 tests and verify they FAIL: `uv run pytest tests/test_manager.py -k "update" -v`

### Implementation for User Story 4

- [X] T041 [US4] Implement `TaskManager.update(task_id: int, title: str | None = None, description: str | None = None) -> Task` in src/manager.py
- [X] T042 [US4] Run US4 tests and verify they PASS: `uv run pytest tests/test_manager.py -k "update" -v`

**Checkpoint**: User Story 4 complete - can update tasks programmatically

---

## Phase 7: User Story 5 - Delete a Task (Priority: P3)

**Goal**: Users can permanently remove tasks by ID

**Independent Test**: Create 3 tasks, delete middle one (ID 2), verify only tasks 1 and 3 remain

### Tests for User Story 5

- [X] T043 [P] [US5] Write unit test for `TaskManager.delete()` with valid ID in tests/test_manager.py
- [X] T044 [P] [US5] Write unit test for `TaskManager.delete()` with invalid ID (TaskNotFoundError) in tests/test_manager.py
- [X] T045 [P] [US5] Write unit test for `TaskManager.delete()` verifying other tasks unchanged in tests/test_manager.py
- [X] T046 [US5] Run US5 tests and verify they FAIL: `uv run pytest tests/test_manager.py -k "delete" -v`

### Implementation for User Story 5

- [X] T047 [US5] Implement `TaskManager.delete(task_id: int) -> None` in src/manager.py
- [X] T048 [US5] Run US5 tests and verify they PASS: `uv run pytest tests/test_manager.py -k "delete" -v`

**Checkpoint**: User Story 5 complete - can delete tasks programmatically

---

## Phase 8: CLI Layer (Menu-Driven Interface)

**Purpose**: Wire all user stories to interactive console interface per FR-009

**Prerequisites**: All user stories (1-5) complete and tested

### Tests for CLI

- [X] T049 [P] Write CLI integration tests for menu display in tests/test_cli.py
- [X] T050 [P] Write CLI integration tests for add_task_flow() in tests/test_cli.py
- [X] T051 [P] Write CLI integration tests for list_tasks_flow() in tests/test_cli.py
- [X] T052 [P] Write CLI integration tests for toggle_task_flow() in tests/test_cli.py
- [X] T053 [P] Write CLI integration tests for update_task_flow() in tests/test_cli.py
- [X] T054 [P] Write CLI integration tests for delete_task_flow() in tests/test_cli.py
- [X] T055 Run CLI tests and verify they FAIL: `uv run pytest tests/test_cli.py -v`

### Implementation for CLI

- [X] T056 Implement `display_menu()` function in src/main.py
- [X] T057 Implement `add_task_flow(manager: TaskManager)` in src/main.py (prompts for title/description)
- [X] T058 Implement `list_tasks_flow(manager: TaskManager)` in src/main.py (formats and displays all tasks)
- [X] T059 Implement `toggle_task_flow(manager: TaskManager)` in src/main.py (prompts for ID)
- [X] T060 Implement `update_task_flow(manager: TaskManager)` in src/main.py (prompts for ID and new values)
- [X] T061 Implement `delete_task_flow(manager: TaskManager)` in src/main.py (prompts for ID)
- [X] T062 Implement `main()` loop with match/case menu dispatch in src/main.py
- [X] T063 Add `if __name__ == "__main__": main()` entry point in src/main.py
- [X] T064 Run CLI tests and verify they PASS: `uv run pytest tests/test_cli.py -v`

**Checkpoint**: Full application working - all 5 operations accessible via menu

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final quality checks

- [X] T065 Run full test suite with coverage: `uv run pytest --cov=src --cov-report=term-missing`
- [X] T066 Verify test coverage >= 80%
- [X] T067 [P] Create README.md with project overview, setup instructions, and usage examples
- [X] T068 [P] Update pyproject.toml with project metadata and entry point script
- [X] T069 Manual validation: Execute all 16 acceptance scenarios from spec.md
- [X] T070 Run quickstart.md validation commands to verify setup instructions work

**Checkpoint**: Production-ready - all acceptance scenarios pass, documentation complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 and US2 are both P1, can run in parallel
  - US3 can start after Foundational (independent of US1/US2)
  - US4 and US5 are both P3, can run in parallel
- **CLI (Phase 8)**: Depends on all user stories (1-5) being complete
- **Polish (Phase 9)**: Depends on CLI being complete

### User Story Dependencies

| Story | Priority | Depends On | Can Parallel With |
|-------|----------|------------|-------------------|
| US1: Add Task | P1 | Foundational | US2 |
| US2: View Tasks | P1 | Foundational | US1 |
| US3: Toggle | P2 | Foundational | US1, US2, US4, US5 |
| US4: Update | P3 | Foundational | US1, US2, US3, US5 |
| US5: Delete | P3 | Foundational | US1, US2, US3, US4 |

### Within Each User Story

1. Tests MUST be written and FAIL before implementation
2. Validation methods before service methods
3. Service methods implement business logic
4. Verify tests PASS after implementation
5. Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003 can run in parallel (different directories)

**Phase 2 (Foundational)**:
- T007, T008 can run in parallel (different classes)
- T010, T011 can run in parallel (different test functions)

**Each User Story**:
- All test tasks marked [P] can run in parallel
- Implementation tasks are sequential within story

**Across User Stories**:
- After Foundational completes, all 5 user stories can theoretically run in parallel
- Recommended: P1 stories first (US1, US2), then P2 (US3), then P3 (US4, US5)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write unit test for TaskManager.add() with valid input in tests/test_manager.py"
Task: "Write unit test for TaskManager.add() with empty title in tests/test_manager.py"
Task: "Write unit test for TaskManager.add() with title at boundary in tests/test_manager.py"

# Then implementation (sequential due to dependencies):
Task: "Implement title validation method in src/models.py"
Task: "Implement description validation method in src/models.py"
Task: "Implement TaskManager.add() in src/manager.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012)
3. Complete Phase 3: User Story 1 - Add Task (T013-T020)
4. Complete Phase 4: User Story 2 - View Tasks (T021-T028)
5. **STOP and VALIDATE**: Can add and view tasks
6. Skip to Phase 8 (CLI) with just add/list operations for quick demo

### Full Delivery (All Features)

1. Complete Setup + Foundational
2. Complete all User Stories in priority order (US1 → US2 → US3 → US4 → US5)
3. Complete CLI Layer
4. Complete Polish

### Single Developer Timeline

Execute phases sequentially: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9

Each phase is independently verifiable with checkpoint tests.

---

## Task Summary

| Phase | Task Range | Count | Description |
|-------|------------|-------|-------------|
| 1: Setup | T001-T005 | 5 | Project initialization |
| 2: Foundational | T006-T012 | 7 | Core models and exceptions |
| 3: US1 Add | T013-T020 | 8 | Add task functionality |
| 4: US2 View | T021-T028 | 8 | View tasks functionality |
| 5: US3 Toggle | T029-T034 | 6 | Toggle completion functionality |
| 6: US4 Update | T035-T042 | 8 | Update task functionality |
| 7: US5 Delete | T043-T048 | 6 | Delete task functionality |
| 8: CLI | T049-T064 | 16 | Menu-driven interface |
| 9: Polish | T065-T070 | 6 | Documentation and validation |
| **Total** | T001-T070 | **70** | |

### Per User Story

| User Story | Tasks | Test Tasks | Implementation Tasks |
|------------|-------|------------|---------------------|
| US1: Add | 8 | 4 | 4 |
| US2: View | 8 | 5 | 3 |
| US3: Toggle | 6 | 4 | 2 |
| US4: Update | 8 | 6 | 2 |
| US5: Delete | 6 | 4 | 2 |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Tests follow TDD: write test → verify fail → implement → verify pass
- Each checkpoint validates story independently
- Commit after each completed task or logical group
- All tasks executable without additional context
