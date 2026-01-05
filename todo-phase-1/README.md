# Todo CLI - Phase I

A command-line Todo application using Python 3.13+ with in-memory storage.

## Features

- **Add Task**: Create tasks with title and optional description
- **List Tasks**: View all tasks with ID, status, and details
- **Update Task**: Modify task title and/or description
- **Delete Task**: Remove tasks permanently
- **Toggle Task**: Mark tasks complete/incomplete

## Requirements

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

```bash
# Navigate to project directory
cd todo-phase-1

# Install dependencies
uv sync
```

## Usage

### Run the Application

```bash
uv run python -m src.main
```

Or via entry point:

```bash
uv run todo
```

### Menu Options

```
=== Todo Manager ===

1. Add Task
2. List Tasks
3. Update Task
4. Delete Task
5. Toggle Task
6. Exit

Select option:
```

### Examples

**Add a Task:**
```
Select option: 1
Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread

Task created with ID: 1
```

**List Tasks:**
```
Select option: 2

=== All Tasks ===

ID: 1 [ ] Buy groceries
   Milk, eggs, bread
```

**Toggle Completion:**
```
Select option: 5
Enter task ID to toggle: 1

Task 1 marked as complete.
```

## Development

### Run Tests

```bash
uv run pytest
```

### Run with Coverage

```bash
uv run pytest --cov=src --cov-report=term-missing
```

## Project Structure

```
todo-phase-1/
├── pyproject.toml      # Project configuration
├── README.md           # This file
├── src/
│   ├── __init__.py     # Package marker
│   ├── models.py       # Domain models (Task, exceptions)
│   ├── manager.py      # Service layer (TaskManager)
│   └── main.py         # CLI interface
└── tests/
    ├── __init__.py     # Package marker
    ├── test_models.py  # Model unit tests
    ├── test_manager.py # Manager unit tests
    └── test_cli.py     # CLI integration tests
```

## Constraints

- In-memory storage only (data is lost when application exits)
- Single-user, single-session
- No persistence, networking, or external dependencies
