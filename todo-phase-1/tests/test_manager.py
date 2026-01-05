"""Unit tests for TaskManager service."""

import pytest
from src.manager import TaskManager
from src.models import Task, TaskNotFoundError, ValidationError


class TestTaskManagerAdd:
    """Tests for TaskManager.add() - User Story 1."""

    def test_add_with_valid_input(self) -> None:
        """Adding task with valid title returns Task with sequential ID."""
        manager = TaskManager()
        task = manager.add("Buy groceries", "Milk, eggs, bread")
        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False

    def test_add_multiple_tasks_sequential_ids(self) -> None:
        """Multiple tasks get sequential IDs starting from 1."""
        manager = TaskManager()
        task1 = manager.add("First")
        task2 = manager.add("Second")
        task3 = manager.add("Third")
        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_with_empty_title_raises_error(self) -> None:
        """Adding task with empty title raises ValidationError."""
        manager = TaskManager()
        with pytest.raises(ValidationError) as exc_info:
            manager.add("")
        assert exc_info.value.field == "title"

    def test_add_with_whitespace_title_raises_error(self) -> None:
        """Adding task with whitespace-only title raises ValidationError."""
        manager = TaskManager()
        with pytest.raises(ValidationError):
            manager.add("   ")

    def test_add_with_title_at_boundary(self) -> None:
        """Adding task with 500-char title succeeds."""
        manager = TaskManager()
        title = "x" * 500
        task = manager.add(title)
        assert len(task.title) == 500

    def test_add_with_title_over_boundary_truncates(self) -> None:
        """Adding task with >500-char title truncates to 500."""
        manager = TaskManager()
        title = "x" * 600
        task = manager.add(title)
        assert len(task.title) == 500

    def test_add_with_default_description(self) -> None:
        """Adding task without description uses empty string."""
        manager = TaskManager()
        task = manager.add("Test task")
        assert task.description == ""


class TestTaskManagerGet:
    """Tests for TaskManager.get() - User Story 2."""

    def test_get_existing_task(self) -> None:
        """Getting an existing task returns the task."""
        manager = TaskManager()
        created = manager.add("Test", "Description")
        retrieved = manager.get(created.id)
        assert retrieved.id == created.id
        assert retrieved.title == "Test"
        assert retrieved.description == "Description"

    def test_get_nonexistent_task_raises_error(self) -> None:
        """Getting non-existent task raises TaskNotFoundError."""
        manager = TaskManager()
        with pytest.raises(TaskNotFoundError) as exc_info:
            manager.get(999)
        assert exc_info.value.task_id == 999


class TestTaskManagerGetAll:
    """Tests for TaskManager.get_all() - User Story 2."""

    def test_get_all_with_multiple_tasks(self) -> None:
        """get_all returns all tasks sorted by ID."""
        manager = TaskManager()
        manager.add("First")
        manager.add("Second")
        manager.add("Third")
        tasks = manager.get_all()
        assert len(tasks) == 3
        assert tasks[0].title == "First"
        assert tasks[1].title == "Second"
        assert tasks[2].title == "Third"

    def test_get_all_empty_returns_empty_list(self) -> None:
        """get_all on empty manager returns empty list."""
        manager = TaskManager()
        tasks = manager.get_all()
        assert tasks == []

    def test_get_all_returns_list_not_dict(self) -> None:
        """get_all returns a list, not dict values."""
        manager = TaskManager()
        manager.add("Test")
        tasks = manager.get_all()
        assert isinstance(tasks, list)


class TestTaskManagerToggle:
    """Tests for TaskManager.toggle() - User Story 3."""

    def test_toggle_incomplete_to_complete(self) -> None:
        """Toggling incomplete task marks it complete."""
        manager = TaskManager()
        task = manager.add("Test")
        assert task.completed is False
        toggled = manager.toggle(task.id)
        assert toggled.completed is True

    def test_toggle_complete_to_incomplete(self) -> None:
        """Toggling complete task marks it incomplete."""
        manager = TaskManager()
        task = manager.add("Test")
        manager.toggle(task.id)  # Now complete
        toggled = manager.toggle(task.id)  # Now incomplete
        assert toggled.completed is False

    def test_toggle_nonexistent_raises_error(self) -> None:
        """Toggling non-existent task raises TaskNotFoundError."""
        manager = TaskManager()
        with pytest.raises(TaskNotFoundError) as exc_info:
            manager.toggle(999)
        assert exc_info.value.task_id == 999


class TestTaskManagerUpdate:
    """Tests for TaskManager.update() - User Story 4."""

    def test_update_title_only(self) -> None:
        """Updating only title preserves description."""
        manager = TaskManager()
        task = manager.add("Original", "Description")
        updated = manager.update(task.id, title="Modified")
        assert updated.title == "Modified"
        assert updated.description == "Description"

    def test_update_description_only(self) -> None:
        """Updating only description preserves title."""
        manager = TaskManager()
        task = manager.add("Title", "Original")
        updated = manager.update(task.id, description="Modified")
        assert updated.title == "Title"
        assert updated.description == "Modified"

    def test_update_both_fields(self) -> None:
        """Updating both title and description works."""
        manager = TaskManager()
        task = manager.add("Original Title", "Original Desc")
        updated = manager.update(task.id, title="New Title", description="New Desc")
        assert updated.title == "New Title"
        assert updated.description == "New Desc"

    def test_update_nonexistent_raises_error(self) -> None:
        """Updating non-existent task raises TaskNotFoundError."""
        manager = TaskManager()
        with pytest.raises(TaskNotFoundError):
            manager.update(999, title="Test")

    def test_update_with_invalid_title_raises_error(self) -> None:
        """Updating with empty title raises ValidationError."""
        manager = TaskManager()
        task = manager.add("Valid")
        with pytest.raises(ValidationError) as exc_info:
            manager.update(task.id, title="")
        assert exc_info.value.field == "title"

    def test_update_preserves_completion_status(self) -> None:
        """Updating title/description doesn't change completion status."""
        manager = TaskManager()
        task = manager.add("Test")
        manager.toggle(task.id)  # Mark complete
        updated = manager.update(task.id, title="Updated")
        assert updated.completed is True


class TestTaskManagerDelete:
    """Tests for TaskManager.delete() - User Story 5."""

    def test_delete_existing_task(self) -> None:
        """Deleting existing task removes it from manager."""
        manager = TaskManager()
        task = manager.add("To delete")
        manager.delete(task.id)
        with pytest.raises(TaskNotFoundError):
            manager.get(task.id)

    def test_delete_nonexistent_raises_error(self) -> None:
        """Deleting non-existent task raises TaskNotFoundError."""
        manager = TaskManager()
        with pytest.raises(TaskNotFoundError) as exc_info:
            manager.delete(999)
        assert exc_info.value.task_id == 999

    def test_delete_preserves_other_tasks(self) -> None:
        """Deleting one task doesn't affect others."""
        manager = TaskManager()
        task1 = manager.add("Keep 1")
        task2 = manager.add("Delete me")
        task3 = manager.add("Keep 2")
        manager.delete(task2.id)
        remaining = manager.get_all()
        assert len(remaining) == 2
        assert remaining[0].id == task1.id
        assert remaining[1].id == task3.id

    def test_delete_does_not_reuse_ids(self) -> None:
        """After deletion, new tasks get new IDs (no reuse)."""
        manager = TaskManager()
        task1 = manager.add("First")
        manager.delete(task1.id)
        task2 = manager.add("Second")
        assert task2.id == 2  # Not 1
