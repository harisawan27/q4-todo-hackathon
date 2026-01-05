# Data Model: Todo In-Memory Python Console App

**Branch**: `001-todo-cli` | **Date**: 2025-12-30 | **Phase**: 1

## Entities

### Task

The primary entity representing a work item to be tracked.

```
+-------------------+
|       Task        |
+-------------------+
| id: int           |  PK, auto-generated, sequential starting at 1
| title: str        |  required, 1-500 characters
| description: str  |  optional, 0-2000 characters, default ""
| completed: bool   |  default False
+-------------------+
```

#### Field Specifications

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| `id` | `int` | Yes | Auto-generated | Positive integer, unique, sequential starting at 1 |
| `title` | `str` | Yes | None | Length: 1-500 characters (inclusive) |
| `description` | `str` | No | `""` | Length: 0-2000 characters (inclusive) |
| `completed` | `bool` | No | `False` | Boolean only |

#### Validation Rules

1. **Title validation (FR-001)**:
   - Must not be empty (whitespace-only counts as empty)
   - Must be between 1 and 500 characters after stripping whitespace
   - Truncate with warning if > 500 characters

2. **Description validation (FR-001)**:
   - May be empty string
   - Must be between 0 and 2000 characters
   - Truncate with warning if > 2000 characters

3. **ID validation (FR-002)**:
   - Must be positive integer
   - Assigned by TaskManager, not user input
   - Sequential starting from 1

#### State Transitions

```
                  toggle()
    [ ] ─────────────────────────► [x]
  incomplete                     complete
    ◄─────────────────────────────
                  toggle()
```

- New tasks start as `completed = False`
- `toggle()` operation flips the boolean value
- No other status values exist in Phase I

---

## Storage Model

### In-Memory Storage (Phase I)

```python
# Type definition
_tasks: dict[int, Task]  # Key: task.id, Value: Task instance
_next_id: int            # Counter for next task ID, starts at 1
```

#### Storage Invariants

1. All keys in `_tasks` match their Task's `id` field
2. `_next_id` is always greater than all existing task IDs
3. No two tasks share the same `id`
4. Task IDs are never reused within a session (gaps allowed after deletion)

#### Example State

```python
# After adding 3 tasks and deleting task 2:
_tasks = {
    1: Task(id=1, title="Buy groceries", description="Milk, eggs", completed=False),
    3: Task(id=3, title="Call mom", description="", completed=True)
}
_next_id = 4
```

---

## Exception Types

### TaskNotFoundError

Raised when an operation references a non-existent task ID.

```python
class TaskNotFoundError(Exception):
    task_id: int    # The ID that was not found
    message: str    # Human-readable error message
```

**Usage**:
- `get(task_id)` when task doesn't exist
- `update(task_id, ...)` when task doesn't exist
- `delete(task_id)` when task doesn't exist
- `toggle(task_id)` when task doesn't exist

### ValidationError

Raised when input fails validation rules.

```python
class ValidationError(Exception):
    field: str      # Field name that failed validation ("title" or "description")
    message: str    # Human-readable error message
```

**Usage**:
- `add(title, ...)` when title is empty or too long
- `update(..., title=...)` when new title is invalid
- `add(..., description=...)` when description is too long
- `update(..., description=...)` when new description is too long

---

## Operations Mapping

| User Story | Operation | Input | Output | Errors |
|------------|-----------|-------|--------|--------|
| US1: Add | `add(title, description)` | title: str, description: str | Task | ValidationError |
| US2: View | `get_all()` | None | list[Task] | None |
| US2: View | `get(task_id)` | task_id: int | Task | TaskNotFoundError |
| US3: Toggle | `toggle(task_id)` | task_id: int | Task | TaskNotFoundError |
| US4: Update | `update(task_id, title, description)` | task_id: int, title?: str, description?: str | Task | TaskNotFoundError, ValidationError |
| US5: Delete | `delete(task_id)` | task_id: int | None | TaskNotFoundError |

---

## Display Format

For `get_all()` list display (per FR-003):

```
ID: {id} [{status}] {title}
   {description (truncated if long)}
```

Where:
- `{status}` = `" "` for incomplete, `"x"` for complete
- `{description}` truncated to 60 characters with "..." if longer

**Example output**:
```
ID: 1 [ ] Buy groceries
   Milk, eggs, bread

ID: 2 [x] Call mom
   (no description)

ID: 3 [ ] Write report
   This is a very long description that will be truncated...
```

---

## Data Constraints Summary

| Constraint | Value | Source |
|------------|-------|--------|
| Max title length | 500 chars | FR-001 |
| Min title length | 1 char | FR-001 |
| Max description length | 2000 chars | FR-001 |
| Min description length | 0 chars | FR-001 |
| Starting task ID | 1 | FR-002 |
| ID increment | +1 (sequential) | FR-002 |
| Default completed | False | Spec |
| ID reuse | Never (within session) | Spec |
