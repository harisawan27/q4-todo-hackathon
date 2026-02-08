"""REST endpoints for direct task CRUD operations."""

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.middleware.auth import get_current_user
from app.models.task import Task, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=list[Task])
async def list_tasks(user_id: str = Depends(get_current_user)):
    """List all tasks for the authenticated user."""
    return await task_service.list_tasks(user_id)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str, user_id: str = Depends(get_current_user)):
    """Get a specific task by ID."""
    task = await task_service.get_task(task_id)
    if task is None or task.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "NOT_FOUND", "message": "Task not found"})
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    updates: TaskUpdate,
    user_id: str = Depends(get_current_user),
    if_match: Optional[str] = Header(None),
):
    """Update a task with optional ETag concurrency control."""
    task = await task_service.update_task(task_id, user_id, updates, etag=if_match)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "NOT_FOUND", "message": "Task not found"})
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, user_id: str = Depends(get_current_user)):
    """Delete a task."""
    deleted = await task_service.delete_task(task_id, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "NOT_FOUND", "message": "Task not found"})


@router.post("/{task_id}/complete", response_model=Task)
async def complete_task(
    task_id: str,
    user_id: str = Depends(get_current_user),
    if_match: Optional[str] = Header(None),
):
    """Mark a task as completed."""
    task = await task_service.complete_task(task_id, user_id, etag=if_match)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "NOT_FOUND", "message": "Task not found"})
    return task
