# Research: Todo In-Memory Python Console App

**Branch**: `001-todo-cli` | **Date**: 2025-12-30 | **Phase**: 0

## Research Summary

This document captures research findings for the Phase I Todo CLI application. Since the technical context was well-defined in the specification, research focused on confirming Python 3.13+ best practices for the implementation patterns.

---

## Research Question 1: Python 3.13+ Dataclass Patterns

**Context**: Need to design Task entity with validation using modern Python patterns.

### Findings

Python 3.13 dataclasses support:
- `@dataclass` decorator with `frozen`, `slots`, `kw_only` parameters
- `field()` function for default values and metadata
- Full type hint support including `|` union syntax

**Recommendation**: Use `@dataclass` without `frozen=True` (need mutable `completed` field), without `slots=True` (marginal benefit for small app).

```python
from dataclasses import dataclass, field

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    completed: bool = False
```

**Validation approach**: Separate class methods rather than `__post_init__`:
- Keeps dataclass simple and focused
- Allows validation to be called explicitly by service layer
- Better testability

### Decision

- **Choice**: Standard `@dataclass` with separate validation methods
- **Rationale**: Simplest approach that meets requirements; validation logic belongs in service layer per Constitution VI (Separation of Concerns)
- **Alternatives rejected**:
  - Pydantic: External dependency forbidden
  - attrs: External dependency forbidden
  - `__post_init__` validation: Mixes concerns, harder to test

---

## Research Question 2: In-Memory Storage Patterns

**Context**: Need efficient storage for tasks with sequential integer ID generation.

### Findings

Options for in-memory task storage:
1. `Dict[int, Task]` - O(1) access by ID
2. `list[Task]` - O(n) search by ID
3. Custom class wrapping dict - Unnecessary abstraction

ID generation options:
1. Counter starting at 1, increment on each add
2. UUID - Violates spec requirement (FR-002: sequential integer)
3. Max ID + 1 - Risk of gaps if items deleted (acceptable per spec)

### Decision

- **Choice**: `Dict[int, Task]` with simple counter starting at 1
- **Rationale**: O(1) operations, matches spec requirement exactly
- **Alternatives rejected**:
  - List: O(n) lookup by ID is unnecessary when dict provides O(1)
  - UUID: Spec requires sequential integers
  - Database: Constitution forbids persistence

**Implementation pattern**:
```python
class TaskManager:
    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1
```

---

## Research Question 3: CLI Menu Patterns

**Context**: Need menu-driven console interface per FR-009.

### Findings

Standard Python CLI patterns:
1. **While loop with match/case** (Python 3.10+)
2. **While loop with if/elif** (Traditional)
3. **argparse with subcommands** (Non-interactive)
4. **curses/blessed** (TUI library, external dependency)

For interactive menu-driven apps, pattern #1 is most Pythonic in Python 3.13:

```python
def main():
    while True:
        display_menu()
        choice = input("Select option: ").strip()
        match choice:
            case "1": add_task_flow()
            case "2": list_tasks_flow()
            case "6" | "q": break
            case _: print("Invalid option")
```

### Decision

- **Choice**: While loop with match/case statement
- **Rationale**: Modern Python syntax, clean and readable, no dependencies
- **Alternatives rejected**:
  - argparse: Not interactive (spec requires menu-driven)
  - curses: External dependency, over-engineered for Phase I
  - if/elif: Less readable than match/case

---

## Research Question 4: Error Handling Patterns

**Context**: Need clear error messages per FR-008 and SC-006.

### Findings

Python error handling options:
1. **Custom exceptions** - Clear semantics, easy to catch
2. **Return codes** - Less Pythonic, harder to compose
3. **Result types** - Over-engineered for simple app
4. **Bare exceptions** - Poor semantics

Custom exception pattern:
```python
class TaskNotFoundError(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")

class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Invalid {field}: {message}")
```

### Decision

- **Choice**: Custom exception classes with meaningful attributes
- **Rationale**: Pythonic, enables CLI layer to format user-friendly messages
- **Alternatives rejected**:
  - Return codes: Not Pythonic
  - Result monad: Over-engineered
  - Generic exceptions: Poor error messages

---

## Research Question 5: Type Hints Best Practices

**Context**: Constitution VIII requires type hints for all function signatures.

### Findings

Python 3.13 type hint features:
- `|` union syntax: `str | None` instead of `Optional[str]`
- Built-in generics: `list[Task]` instead of `List[Task]`
- `Self` type for methods returning class instance
- No need for `from __future__ import annotations`

**Recommended style**:
```python
def update(self, task_id: int, title: str | None = None, description: str | None = None) -> Task:
    ...

def get_all(self) -> list[Task]:
    ...
```

### Decision

- **Choice**: Modern Python 3.13 type hint syntax
- **Rationale**: Cleaner, no imports needed from typing for basic types
- **Imports needed**: Only `from dataclasses import dataclass, field`

---

## Consolidated Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Entity design | `@dataclass` without slots/frozen | Simple, mutable completed field |
| Validation | Class methods, separate from dataclass | Separation of concerns |
| Storage | `Dict[int, Task]` | O(1) access, matches spec |
| ID generation | Counter starting at 1 | Matches FR-002 |
| CLI pattern | While loop + match/case | Modern Python, clean |
| Error handling | Custom exceptions | Clear semantics |
| Type hints | Python 3.13 syntax (no Optional) | Modern, cleaner |

---

## Dependencies Confirmed

**Production dependencies**: None (standard library only)

**Development dependencies**:
- pytest >= 8.0 (testing)
- pytest-cov >= 4.0 (coverage reporting)

---

## Next Steps

1. Proceed to Phase 1: Data Model design
2. Generate `data-model.md` with entity specification
3. Generate `quickstart.md` with setup instructions
