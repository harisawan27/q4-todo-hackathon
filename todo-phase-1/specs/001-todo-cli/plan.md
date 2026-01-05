# Implementation Plan: Todo In-Memory Python Console App

**Branch**: `001-todo-cli` | **Date**: 2025-12-30 | **Spec**: [specs/001-todo-cli/spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-cli/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

A command-line Todo application using Python 3.13+ with in-memory storage. The application provides menu-driven CRUD operations for task management: Add, View, Update, Delete, and Toggle completion status. Data exists only during runtime with no persistence. The implementation follows a clean three-layer architecture (Domain, Service, CLI) using standard library only.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only: dataclasses, typing, sys)
**Storage**: In-memory dictionary (Dict[int, Task])
**Testing**: pytest with pytest-cov
**Target Platform**: Cross-platform console (Windows, macOS, Linux)
**Project Type**: Single project
**Performance Goals**: <1 second response time for all operations (per SC-008)
**Constraints**: No file I/O, no network, no external services, in-memory only
**Scale/Scope**: Single-user, single-session, ~100s of tasks max practical limit

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Project Scope** | ✅ PASS | Standalone, in-memory CLI app matches Phase I scope |
| **II. Functional Requirements** | ✅ PASS | Spec includes exactly: Add, View, Update, Delete, Toggle - no extras |
| **III. Non-Goals** | ✅ PASS | No persistence, web, auth, AI, async, network in spec |
| **IV. Technical Constraints** | ✅ PASS | Python 3.13+, in-memory dict, console I/O, standard library only |
| **V. Spec-Driven Development** | ✅ PASS | Constitution → Spec → Plan → Tasks → Implementation order followed |
| **VI. Separation of Concerns** | ✅ PASS | Plan defines Domain/Service/CLI layers |
| **VII. Reusable Intelligence** | ✅ PASS | Will use `.claude/skills/` and `.claude/agents/` |
| **VIII. Code Quality Standards** | ✅ PASS | Type hints, PEP 8, no dead code requirements acknowledged |
| **IX. AI Behavior Rules** | ✅ PASS | No scope creep, clarification required for ambiguity |
| **X. Documentation Requirements** | ✅ PASS | README.md, CLAUDE.md, specs/ will be created |

**GATE STATUS**: ✅ ALL CHECKS PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-cli/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py          # Package marker
├── models.py            # Domain layer: Task dataclass, validation
├── manager.py           # Service layer: TaskManager class (CRUD + toggle)
└── main.py              # CLI layer: Menu loop, I/O handling

tests/
├── __init__.py          # Package marker
├── test_models.py       # Unit tests for Task entity
├── test_manager.py      # Unit tests for TaskManager operations
└── test_cli.py          # Integration tests for CLI behavior
```

**Structure Decision**: Single project structure selected per Constitution Section VI. Three files map directly to the three-layer architecture:
- `models.py` = Domain layer (Task entity definition, validation rules)
- `manager.py` = Service layer (Task operations: CRUD, toggle)
- `main.py` = CLI layer (User input parsing, output formatting)

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

**Note**: All Constitution checks pass. No violations requiring justification.

---

## Phase 0: Research

### Research Questions

Since the Technical Context has no NEEDS CLARIFICATION items, Phase 0 focuses on confirming best practices:

1. **Python 3.13+ dataclass patterns** - How to use `@dataclass` with field validation
2. **In-memory storage patterns** - Best practices for Dict-based storage with ID generation
3. **CLI menu patterns** - Standard input/output handling in Python console apps
4. **Type hints** - Modern Python typing conventions for Phase I scope

### Research Findings

**Decision 1: Task Entity Design**
- Use `@dataclass(frozen=False)` to allow mutable status updates
- Use `field()` with `default_factory` for default values
- Validation logic as class methods, not `__post_init__` (keep dataclass simple)
- **Rationale**: Clean separation; validation can be called explicitly
- **Alternatives rejected**: Pydantic (external dependency), attrs (external dependency)

**Decision 2: ID Generation**
- Use simple integer counter in TaskManager, starting at 1
- ID stored in manager, not in Task class itself during creation
- **Rationale**: Matches spec requirement (FR-002: sequential integer starting from 1)
- **Alternatives rejected**: UUID (overkill, violates spec), hash-based (unnecessary complexity)

**Decision 3: Storage Pattern**
- `Dict[int, Task]` keyed by task ID
- Direct access O(1) for all operations
- **Rationale**: Simplest pattern that meets all requirements
- **Alternatives rejected**: List with linear search (slower), SQLite (forbidden by Constitution)

**Decision 4: CLI Pattern**
- Infinite loop with numbered menu
- Functions for each operation returning success/error messages
- `input()` for user interaction, `print()` for output
- **Rationale**: Standard Python CLI pattern, meets FR-009
- **Alternatives rejected**: argparse commands (less interactive), curses (complexity)

**Decision 5: Error Handling**
- Custom exceptions for domain errors: `TaskNotFoundError`, `ValidationError`
- CLI catches and displays user-friendly messages
- **Rationale**: Clean error propagation from service to CLI layer
- **Alternatives rejected**: Return codes (less Pythonic), bare exceptions (unclear semantics)

---

## Phase 1: Design

### Data Model

See `data-model.md` for full entity specification.

### API Contracts

For Phase I (CLI app), no formal API contracts are needed since there's no external interface. The internal contracts are:

**TaskManager Public Interface:**
```python
class TaskManager:
    def add(self, title: str, description: str = "") -> Task
    def get(self, task_id: int) -> Task
    def get_all(self) -> list[Task]
    def update(self, task_id: int, title: str | None = None, description: str | None = None) -> Task
    def delete(self, task_id: int) -> None
    def toggle(self, task_id: int) -> Task
```

**Error Types:**
- `TaskNotFoundError(task_id: int)` - Raised when task ID doesn't exist
- `ValidationError(field: str, message: str)` - Raised for invalid input

### Quickstart

See `quickstart.md` for environment setup and usage instructions.

---

## Development Phases

### Phase A: Scaffolding

**Objective**: Set up project structure with uv and create skeleton files.

**Steps**:
1. Initialize uv project: `uv init`
2. Configure pyproject.toml for Python 3.13+
3. Create directory structure: `src/`, `tests/`
4. Create `__init__.py` files
5. Add pytest as dev dependency: `uv add --dev pytest pytest-cov`

**Checkpoint**: `uv run python -c "import src"` succeeds

### Phase B: Domain Layer (models.py)

**Objective**: Implement Task dataclass with validation.

**Steps**:
1. Create `Task` dataclass with fields: id, title, description, completed
2. Implement `validate_title()` class method (1-500 chars)
3. Implement `validate_description()` class method (0-2000 chars)
4. Create `TaskNotFoundError` exception
5. Create `ValidationError` exception

**Checkpoint**: All test_models.py tests pass

### Phase C: Service Layer (manager.py)

**Objective**: Implement TaskManager with all CRUD operations.

**Steps**:
1. Create TaskManager class with `_tasks: Dict[int, Task]` and `_next_id: int`
2. Implement `add()` - validates, creates Task, stores, returns
3. Implement `get()` - raises TaskNotFoundError if missing
4. Implement `get_all()` - returns list of all tasks
5. Implement `update()` - validates, updates fields, returns
6. Implement `delete()` - raises TaskNotFoundError if missing
7. Implement `toggle()` - flips completed status, returns

**Checkpoint**: All test_manager.py tests pass

### Phase D: CLI Layer (main.py)

**Objective**: Implement menu-driven console interface.

**Steps**:
1. Create `display_menu()` function
2. Create `add_task_flow()` - prompts for title/description
3. Create `list_tasks_flow()` - formats and displays all tasks
4. Create `update_task_flow()` - prompts for ID and new values
5. Create `delete_task_flow()` - prompts for ID, confirms
6. Create `toggle_task_flow()` - prompts for ID
7. Create `main()` loop with menu dispatch
8. Add `if __name__ == "__main__"` entry point

**Checkpoint**: Manual testing of all 5 operations + exit

### Phase E: Validation & Polish

**Objective**: Ensure all acceptance scenarios pass.

**Steps**:
1. Run full test suite with coverage: `uv run pytest --cov=src`
2. Verify each user story acceptance scenario manually
3. Fix any edge case failures
4. Create/update README.md with usage instructions

**Checkpoint**: 100% of acceptance scenarios pass, test coverage > 80%

---

## Verification Matrix

| User Story | Test File | Acceptance Scenarios | Status |
|------------|-----------|---------------------|--------|
| US1: Add Task | test_manager.py, test_cli.py | 3 scenarios | Pending |
| US2: View Tasks | test_manager.py, test_cli.py | 3 scenarios | Pending |
| US3: Toggle Task | test_manager.py, test_cli.py | 3 scenarios | Pending |
| US4: Update Task | test_manager.py, test_cli.py | 4 scenarios | Pending |
| US5: Delete Task | test_manager.py, test_cli.py | 3 scenarios | Pending |

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| Input validation edge cases | Comprehensive unit tests with boundary values |
| CLI input/output testing | Use pytest fixtures to mock stdin/stdout |
| Scope creep | Strict adherence to Constitution; reject non-spec features |

---

## Post-Design Constitution Re-Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| **II. Functional Requirements** | ✅ PASS | Design implements exactly 5 features: Add, View, Update, Delete, Toggle |
| **III. Non-Goals** | ✅ PASS | No persistence, web, auth, AI, async, network in design |
| **VI. Separation of Concerns** | ✅ PASS | Three clear layers: models.py (Domain), manager.py (Service), main.py (CLI) |
| **VII. Reusable Intelligence** | ✅ PASS | Design aligns with `.claude/skills/` contracts |
| **VIII. Code Quality Standards** | ✅ PASS | Type hints planned, PEP 8 required, no dead code |

**FINAL GATE STATUS**: ✅ ALL CHECKS PASS - Ready for task generation
