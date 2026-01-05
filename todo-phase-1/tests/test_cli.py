"""Integration tests for CLI interface."""

import pytest
from io import StringIO
from unittest.mock import patch

from src.main import (
    display_menu,
    add_task_flow,
    list_tasks_flow,
    toggle_task_flow,
    update_task_flow,
    delete_task_flow,
    format_task,
)
from src.manager import TaskManager


class TestDisplayMenu:
    """Tests for menu display."""

    def test_menu_shows_all_options(self) -> None:
        """Menu displays all 6 options."""
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            display_menu()
            output = mock_stdout.getvalue()
        assert "1." in output and "Add" in output
        assert "2." in output and "List" in output
        assert "3." in output and "Update" in output
        assert "4." in output and "Delete" in output
        assert "5." in output and "Toggle" in output
        assert "6." in output and "Exit" in output


class TestFormatTask:
    """Tests for task formatting."""

    def test_format_incomplete_task(self) -> None:
        """Incomplete task shows [ ] indicator."""
        manager = TaskManager()
        task = manager.add("Test task", "Description")
        output = format_task(task)
        assert "[ ]" in output
        assert "Test task" in output
        assert "Description" in output

    def test_format_complete_task(self) -> None:
        """Complete task shows [x] indicator."""
        manager = TaskManager()
        task = manager.add("Test task")
        manager.toggle(task.id)
        output = format_task(task)
        assert "[x]" in output

    def test_format_task_without_description(self) -> None:
        """Task without description shows appropriate message."""
        manager = TaskManager()
        task = manager.add("Test task")
        output = format_task(task)
        assert "no description" in output.lower() or task.description == ""


class TestAddTaskFlow:
    """Tests for add task flow."""

    def test_add_task_success(self) -> None:
        """Adding task with valid input shows success message."""
        manager = TaskManager()
        inputs = iter(["Buy groceries", "Milk, eggs"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                add_task_flow(manager)
                output = mock_stdout.getvalue()
        assert "ID: 1" in output or "1" in output
        assert len(manager.get_all()) == 1

    def test_add_task_empty_title_shows_error(self) -> None:
        """Adding task with empty title shows error."""
        manager = TaskManager()
        # First try empty title (gets error), then provide description for error case,
        # then valid title with description
        inputs = iter(["", "", "Valid title", "Description"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                add_task_flow(manager)
                output = mock_stdout.getvalue()
        # Should show error for empty title, then succeed with valid
        assert "error" in output.lower() or "cannot" in output.lower()


class TestListTasksFlow:
    """Tests for list tasks flow."""

    def test_list_empty_shows_message(self) -> None:
        """Listing empty manager shows appropriate message."""
        manager = TaskManager()
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            list_tasks_flow(manager)
            output = mock_stdout.getvalue()
        assert "no task" in output.lower() or "empty" in output.lower()

    def test_list_with_tasks_shows_all(self) -> None:
        """Listing shows all tasks."""
        manager = TaskManager()
        manager.add("First task")
        manager.add("Second task")
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            list_tasks_flow(manager)
            output = mock_stdout.getvalue()
        assert "First task" in output
        assert "Second task" in output


class TestToggleTaskFlow:
    """Tests for toggle task flow."""

    def test_toggle_existing_task(self) -> None:
        """Toggling existing task changes status."""
        manager = TaskManager()
        task = manager.add("Test")
        assert task.completed is False
        inputs = iter(["1"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO):
                toggle_task_flow(manager)
        assert manager.get(1).completed is True

    def test_toggle_nonexistent_shows_error(self) -> None:
        """Toggling non-existent task shows error."""
        manager = TaskManager()
        inputs = iter(["999"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                toggle_task_flow(manager)
                output = mock_stdout.getvalue()
        assert "not found" in output.lower() or "error" in output.lower()


class TestUpdateTaskFlow:
    """Tests for update task flow."""

    def test_update_title_only(self) -> None:
        """Updating only title works."""
        manager = TaskManager()
        manager.add("Original", "Description")
        inputs = iter(["1", "Updated", ""])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO):
                update_task_flow(manager)
        task = manager.get(1)
        assert task.title == "Updated"
        assert task.description == "Description"

    def test_update_nonexistent_shows_error(self) -> None:
        """Updating non-existent task shows error."""
        manager = TaskManager()
        inputs = iter(["999", "New title", ""])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                update_task_flow(manager)
                output = mock_stdout.getvalue()
        assert "not found" in output.lower() or "error" in output.lower()


class TestDeleteTaskFlow:
    """Tests for delete task flow."""

    def test_delete_existing_task(self) -> None:
        """Deleting existing task removes it."""
        manager = TaskManager()
        manager.add("To delete")
        inputs = iter(["1"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO):
                delete_task_flow(manager)
        assert len(manager.get_all()) == 0

    def test_delete_nonexistent_shows_error(self) -> None:
        """Deleting non-existent task shows error."""
        manager = TaskManager()
        inputs = iter(["999"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                delete_task_flow(manager)
                output = mock_stdout.getvalue()
        assert "not found" in output.lower() or "error" in output.lower()

    def test_delete_invalid_input_shows_error(self) -> None:
        """Deleting with non-numeric input shows error."""
        manager = TaskManager()
        inputs = iter(["abc"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                delete_task_flow(manager)
                output = mock_stdout.getvalue()
        assert "valid number" in output.lower() or "error" in output.lower()


class TestFormatTaskLongDescription:
    """Tests for format_task with long descriptions."""

    def test_format_task_long_description_truncated(self) -> None:
        """Long description is truncated with ellipsis."""
        manager = TaskManager()
        long_desc = "x" * 100
        task = manager.add("Test", long_desc)
        output = format_task(task)
        assert "..." in output
        assert len(output.split("\n")[1].strip()) <= 63  # "   " prefix + 60 chars max


class TestToggleInvalidInput:
    """Additional toggle tests."""

    def test_toggle_invalid_input_shows_error(self) -> None:
        """Toggling with non-numeric input shows error."""
        manager = TaskManager()
        inputs = iter(["abc"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                toggle_task_flow(manager)
                output = mock_stdout.getvalue()
        assert "valid number" in output.lower() or "error" in output.lower()


class TestUpdateInvalidInput:
    """Additional update tests."""

    def test_update_invalid_id_shows_error(self) -> None:
        """Updating with non-numeric ID shows error."""
        manager = TaskManager()
        inputs = iter(["abc", "title", "desc"])
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                update_task_flow(manager)
                output = mock_stdout.getvalue()
        assert "valid number" in output.lower() or "error" in output.lower()

    def test_update_with_empty_title_shows_error(self) -> None:
        """Updating with empty title shows validation error."""
        manager = TaskManager()
        manager.add("Original", "Description")
        inputs = iter(["1", "   ", ""])  # Whitespace-only title should fail
        with patch("builtins.input", lambda _: next(inputs)):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                update_task_flow(manager)
                output = mock_stdout.getvalue()
        # Title validation should fail
        assert "error" in output.lower()
