"""Task CRUD endpoints"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.jwt_bearer import CurrentUser, get_current_user
from app.database import get_session
from app.models.task import Task, TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


def get_task_by_id_for_user(
    task_id: str, user_id: str, session: Session
) -> Task | None:
    """Helper to get a task ensuring it belongs to the user.
    Returns None if not found OR not owned by user (prevents enumeration).
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    return session.exec(statement).first()


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[Task]:
    """List all tasks for the authenticated user, ordered by created_at DESC"""
    statement = (
        select(Task)
        .where(Task.user_id == current_user.user_id)
        .order_by(Task.created_at.desc())
    )
    tasks = session.exec(statement).all()
    return list(tasks)


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    """Create a new task for the authenticated user - only title is required"""
    task = Task(
        title=task_data.title,
        user_id=current_user.user_id,
        description=task_data.description,
        due_date=task_data.due_date,
        priority=task_data.priority.value if task_data.priority else None,
        tags=task_data.tags if task_data.tags else [],
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    """Get a specific task by ID (must be owned by user)"""
    task = get_task_by_id_for_user(task_id, current_user.user_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    """Update a task (full replacement of provided fields)"""
    task = get_task_by_id_for_user(task_id, current_user.user_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def patch_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    """Partially update a task"""
    task = get_task_by_id_for_user(task_id, current_user.user_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Update only provided fields
    update_data = task_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a task"""
    task = get_task_by_id_for_user(task_id, current_user.user_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    session.delete(task)
    session.commit()


@router.post("/{task_id}/toggle", response_model=TaskRead)
async def toggle_task(
    task_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Task:
    """Toggle the completion status of a task"""
    task = get_task_by_id_for_user(task_id, current_user.user_id, session)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    task.completed = not task.completed
    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
