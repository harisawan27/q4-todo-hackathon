"""Task manager service for CRUD operations."""

from src.models import Task, TaskNotFoundError, ValidationError, validate_title, validate_description


class TaskManager:
    """Manages tasks in memory with CRUD and toggle operations.

    Attributes:
        _tasks: Dictionary mapping task IDs to Task instances
        _next_id: Counter for generating sequential task IDs
    """

    def __init__(self) -> None:
        """Initialize an empty task manager."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add(self, title: str, description: str = "") -> Task:
        """Add a new task.

        Args:
            title: Task title (1-500 characters)
            description: Task description (0-2000 characters, default "")

        Returns:
            The created Task with assigned ID

        Raises:
            ValidationError: If title is empty or inputs are invalid
        """
        validated_title = validate_title(title)
        validated_description = validate_description(description)

        task = Task(
            id=self._next_id,
            title=validated_title,
            description=validated_description,
            completed=False,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get(self, task_id: int) -> Task:
        """Get a task by ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            The Task with the specified ID

        Raises:
            TaskNotFoundError: If no task exists with the given ID
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all(self) -> list[Task]:
        """Get all tasks.

        Returns:
            List of all tasks, sorted by ID
        """
        return sorted(self._tasks.values(), key=lambda t: t.id)

    def update(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """Update a task's title and/or description.

        Args:
            task_id: The ID of the task to update
            title: New title (None to keep current)
            description: New description (None to keep current)

        Returns:
            The updated Task

        Raises:
            TaskNotFoundError: If no task exists with the given ID
            ValidationError: If the new title is invalid
        """
        task = self.get(task_id)

        if title is not None:
            task.title = validate_title(title)
        if description is not None:
            task.description = validate_description(description)

        return task

    def delete(self, task_id: int) -> None:
        """Delete a task by ID.

        Args:
            task_id: The ID of the task to delete

        Raises:
            TaskNotFoundError: If no task exists with the given ID
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]

    def toggle(self, task_id: int) -> Task:
        """Toggle a task's completion status.

        Args:
            task_id: The ID of the task to toggle

        Returns:
            The updated Task with toggled completion status

        Raises:
            TaskNotFoundError: If no task exists with the given ID
        """
        task = self.get(task_id)
        task.completed = not task.completed
        return task
