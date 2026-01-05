"""Command-line interface for the Todo application."""

import sys
from src.manager import TaskManager
from src.models import Task, TaskNotFoundError, ValidationError


def display_menu() -> None:
    """Display the main menu options."""
    print("\n=== Todo Manager ===\n")
    print("1. Add Task")
    print("2. List Tasks")
    print("3. Update Task")
    print("4. Delete Task")
    print("5. Toggle Task")
    print("6. Exit")
    print()


def format_task(task: Task) -> str:
    """Format a task for display.

    Args:
        task: The task to format

    Returns:
        Formatted string representation
    """
    status = "x" if task.completed else " "
    desc = task.description if task.description else "(no description)"
    if len(desc) > 60:
        desc = desc[:57] + "..."
    return f"ID: {task.id} [{status}] {task.title}\n   {desc}"


def add_task_flow(manager: TaskManager) -> None:
    """Interactive flow for adding a task.

    Args:
        manager: The TaskManager instance
    """
    while True:
        title = input("Enter task title: ")
        try:
            description = input("Enter description (optional): ")
            task = manager.add(title, description)
            print(f"\nTask created with ID: {task.id}")
            break
        except ValidationError as e:
            print(f"\nError: {e.message}")
            print("Please try again.\n")


def list_tasks_flow(manager: TaskManager) -> None:
    """Interactive flow for listing all tasks.

    Args:
        manager: The TaskManager instance
    """
    tasks = manager.get_all()
    if not tasks:
        print("\nNo tasks found. Add some tasks first!")
        return

    print("\n=== All Tasks ===\n")
    for task in tasks:
        print(format_task(task))
        print()


def toggle_task_flow(manager: TaskManager) -> None:
    """Interactive flow for toggling task completion.

    Args:
        manager: The TaskManager instance
    """
    try:
        task_id = int(input("Enter task ID to toggle: "))
        task = manager.toggle(task_id)
        status = "complete" if task.completed else "incomplete"
        print(f"\nTask {task_id} marked as {status}.")
    except ValueError:
        print("\nError: Please enter a valid number.")
    except TaskNotFoundError as e:
        print(f"\nError: {e.message}")


def update_task_flow(manager: TaskManager) -> None:
    """Interactive flow for updating a task.

    Args:
        manager: The TaskManager instance
    """
    try:
        task_id = int(input("Enter task ID to update: "))
        new_title = input("Enter new title (press Enter to keep current): ")
        new_description = input("Enter new description (press Enter to keep current): ")

        title = new_title if new_title else None
        description = new_description if new_description else None

        manager.update(task_id, title=title, description=description)
        print(f"\nTask {task_id} updated successfully.")
    except ValueError:
        print("\nError: Please enter a valid number.")
    except TaskNotFoundError as e:
        print(f"\nError: {e.message}")
    except ValidationError as e:
        print(f"\nError: {e.message}")


def delete_task_flow(manager: TaskManager) -> None:
    """Interactive flow for deleting a task.

    Args:
        manager: The TaskManager instance
    """
    try:
        task_id = int(input("Enter task ID to delete: "))
        manager.delete(task_id)
        print(f"\nTask {task_id} deleted successfully.")
    except ValueError:
        print("\nError: Please enter a valid number.")
    except TaskNotFoundError as e:
        print(f"\nError: {e.message}")


def main() -> None:
    """Main entry point for the Todo CLI application."""
    manager = TaskManager()

    while True:
        display_menu()
        choice = input("Select option: ")

        match choice:
            case "1":
                add_task_flow(manager)
            case "2":
                list_tasks_flow(manager)
            case "3":
                update_task_flow(manager)
            case "4":
                delete_task_flow(manager)
            case "5":
                toggle_task_flow(manager)
            case "6":
                print("\nGoodbye!")
                sys.exit(0)
            case _:
                print("\nInvalid option. Please try again.")


if __name__ == "__main__":
    main()
