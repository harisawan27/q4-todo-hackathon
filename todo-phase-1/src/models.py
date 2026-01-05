"""Domain models for the Todo application."""

from dataclasses import dataclass, field


class TaskNotFoundError(Exception):
    """Raised when a task with the specified ID does not exist."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        self.message = f"Task with ID {task_id} not found"
        super().__init__(self.message)


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, field_name: str, message: str) -> None:
        self.field = field_name
        self.message = message
        super().__init__(f"{field_name}: {message}")


@dataclass
class Task:
    """Represents a todo task.

    Attributes:
        id: Unique identifier (positive integer, sequential starting at 1)
        title: Task title (1-500 characters, required)
        description: Task description (0-2000 characters, optional)
        completed: Whether the task is complete (default False)
    """

    id: int
    title: str
    description: str = ""
    completed: bool = field(default=False)


def validate_title(title: str) -> str:
    """Validate and normalize a task title.

    Args:
        title: The title to validate

    Returns:
        The stripped title if valid

    Raises:
        ValidationError: If title is empty or whitespace-only
    """
    stripped = title.strip()
    if not stripped:
        raise ValidationError("title", "Title cannot be empty")
    if len(stripped) > 500:
        stripped = stripped[:500]
    return stripped


def validate_description(description: str) -> str:
    """Validate and normalize a task description.

    Args:
        description: The description to validate

    Returns:
        The stripped description, truncated if necessary

    Raises:
        ValidationError: If description is not a string
    """
    stripped = description.strip()
    if len(stripped) > 2000:
        stripped = stripped[:2000]
    return stripped
