# Quickstart: Todo In-Memory Python Console App

**Branch**: `001-todo-cli` | **Date**: 2025-12-30 | **Phase**: 1

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/) package manager

## Environment Setup

### 1. Initialize Project with uv

```bash
# Navigate to project directory
cd todo-phase-1

# Initialize uv project (if not already initialized)
uv init

# Verify Python version
uv run python --version
# Should output: Python 3.13.x
```

### 2. Configure pyproject.toml

Ensure `pyproject.toml` contains:

```toml
[project]
name = "todo-cli"
version = "0.1.0"
description = "Phase I Todo In-Memory Python Console App"
requires-python = ">=3.13"
dependencies = []

[project.scripts]
todo = "src.main:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80
```

### 3. Install Development Dependencies

```bash
# Add pytest and coverage as dev dependencies
uv add --dev pytest pytest-cov
```

### 4. Create Directory Structure

```bash
# Create source directory
mkdir -p src tests

# Create package markers
touch src/__init__.py
touch tests/__init__.py
```

## Running the Application

### Start the Todo CLI

```bash
# Run the main module
uv run python -m src.main
```

Or after installation:

```bash
# Run via entry point
uv run todo
```

### Expected Output

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

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run with Coverage

```bash
uv run pytest --cov=src --cov-report=term-missing
```

### Run Specific Test File

```bash
uv run pytest tests/test_models.py
uv run pytest tests/test_manager.py
uv run pytest tests/test_cli.py
```

### Run with Verbose Output

```bash
uv run pytest -v
```

## Usage Examples

### Add a Task

```
Select option: 1
Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread

Task created with ID: 1
```

### List All Tasks

```
Select option: 2

=== All Tasks ===
ID: 1 [ ] Buy groceries
   Milk, eggs, bread

ID: 2 [x] Call mom
   (no description)
```

### Toggle Task Completion

```
Select option: 5
Enter task ID to toggle: 1

Task 1 marked as complete.
```

### Update a Task

```
Select option: 3
Enter task ID to update: 1
Enter new title (press Enter to keep current): Buy groceries and snacks
Enter new description (press Enter to keep current):

Task 1 updated successfully.
```

### Delete a Task

```
Select option: 4
Enter task ID to delete: 2

Task 2 deleted successfully.
```

### Exit

```
Select option: 6

Goodbye!
```

## Validation Commands

### Verify Installation

```bash
# Check uv is working
uv --version

# Check Python version
uv run python --version

# Check package can be imported
uv run python -c "import src; print('OK')"
```

### Verify Test Setup

```bash
# Check pytest is installed
uv run pytest --version

# Run tests with verbose output
uv run pytest -v

# Check coverage configuration
uv run pytest --cov=src --cov-report=term
```

## Troubleshooting

### "Module not found" Error

Ensure `__init__.py` exists in both `src/` and `tests/` directories.

### Python Version Mismatch

```bash
# Check available Python versions
uv python list

# Pin Python version
uv python pin 3.13
```

### Test Discovery Issues

Ensure test files are named `test_*.py` and test functions are named `test_*`.

## Project Structure After Setup

```
todo-phase-1/
├── pyproject.toml
├── uv.lock
├── README.md
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── manager.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_manager.py
│   └── test_cli.py
└── specs/
    └── 001-todo-cli/
        ├── spec.md
        ├── plan.md
        ├── research.md
        ├── data-model.md
        └── quickstart.md
```
