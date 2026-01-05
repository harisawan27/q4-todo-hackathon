"""Unit tests for domain models."""

import pytest
from src.models import Task, TaskNotFoundError, ValidationError, validate_title, validate_description


class TestTask:
    """Tests for the Task dataclass."""

    def test_task_creation_with_all_fields(self) -> None:
        """Task can be created with all fields specified."""
        task = Task(id=1, title="Test", description="Description", completed=True)
        assert task.id == 1
        assert task.title == "Test"
        assert task.description == "Description"
        assert task.completed is True

    def test_task_creation_with_defaults(self) -> None:
        """Task has correct default values for optional fields."""
        task = Task(id=1, title="Test")
        assert task.description == ""
        assert task.completed is False

    def test_task_is_mutable(self) -> None:
        """Task fields can be modified after creation."""
        task = Task(id=1, title="Original")
        task.title = "Modified"
        task.completed = True
        assert task.title == "Modified"
        assert task.completed is True


class TestTaskNotFoundError:
    """Tests for TaskNotFoundError exception."""

    def test_stores_task_id(self) -> None:
        """Exception stores the task_id that was not found."""
        error = TaskNotFoundError(42)
        assert error.task_id == 42

    def test_has_descriptive_message(self) -> None:
        """Exception has a human-readable message."""
        error = TaskNotFoundError(42)
        assert "42" in error.message
        assert "not found" in error.message.lower()

    def test_can_be_raised_and_caught(self) -> None:
        """Exception can be raised and caught."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            raise TaskNotFoundError(99)
        assert exc_info.value.task_id == 99


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_stores_field_name(self) -> None:
        """Exception stores the field that failed validation."""
        error = ValidationError("title", "Cannot be empty")
        assert error.field == "title"

    def test_stores_message(self) -> None:
        """Exception stores the validation message."""
        error = ValidationError("title", "Cannot be empty")
        assert error.message == "Cannot be empty"

    def test_can_be_raised_and_caught(self) -> None:
        """Exception can be raised and caught."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("description", "Too long")
        assert exc_info.value.field == "description"


class TestValidateTitle:
    """Tests for title validation function."""

    def test_valid_title(self) -> None:
        """Valid title is returned stripped."""
        assert validate_title("  Buy groceries  ") == "Buy groceries"

    def test_empty_title_raises_error(self) -> None:
        """Empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_title("")
        assert exc_info.value.field == "title"

    def test_whitespace_only_raises_error(self) -> None:
        """Whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError):
            validate_title("   ")

    def test_title_at_max_length(self) -> None:
        """Title at exactly 500 chars is valid."""
        title = "x" * 500
        assert validate_title(title) == title

    def test_title_exceeds_max_is_truncated(self) -> None:
        """Title over 500 chars is truncated."""
        title = "x" * 600
        result = validate_title(title)
        assert len(result) == 500


class TestValidateDescription:
    """Tests for description validation function."""

    def test_valid_description(self) -> None:
        """Valid description is returned stripped."""
        assert validate_description("  Some notes  ") == "Some notes"

    def test_empty_description_is_valid(self) -> None:
        """Empty description is allowed."""
        assert validate_description("") == ""

    def test_description_at_max_length(self) -> None:
        """Description at exactly 2000 chars is valid."""
        desc = "y" * 2000
        assert validate_description(desc) == desc

    def test_description_exceeds_max_is_truncated(self) -> None:
        """Description over 2000 chars is truncated."""
        desc = "y" * 2500
        result = validate_description(desc)
        assert len(result) == 2000
