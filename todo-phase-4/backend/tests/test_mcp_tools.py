"""Tests for MCP tools"""

import pytest
from uuid import uuid4

from sqlmodel import Session

from app.models import Task
from app.mcp.tools import (
    list_tasks,
    add_task,
    complete_task,
    update_task,
    delete_task,
    find_task_by_title,
)


class TestListTasks:
    """Tests for list_tasks tool"""

    def test_list_tasks_all(self, session: Session, user_id: str, multiple_tasks):
        """Test listing all tasks"""
        # Patch the engine in tools module
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = list_tasks(user_id, "all")

            assert "tasks" in result
            assert result["count"] == 5
            assert result["status_filter"] == "all"
        finally:
            tools_module.engine = original_engine

    def test_list_tasks_pending(self, session: Session, user_id: str, multiple_tasks):
        """Test listing only pending tasks"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = list_tasks(user_id, "pending")

            assert "tasks" in result
            assert result["count"] == 3
            assert all(not t["completed"] for t in result["tasks"])
        finally:
            tools_module.engine = original_engine

    def test_list_tasks_completed(self, session: Session, user_id: str, multiple_tasks):
        """Test listing only completed tasks"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = list_tasks(user_id, "completed")

            assert "tasks" in result
            assert result["count"] == 2
            assert all(t["completed"] for t in result["tasks"])
        finally:
            tools_module.engine = original_engine

    def test_list_tasks_empty(self, session: Session, user_id: str):
        """Test listing tasks when user has none"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = list_tasks(user_id, "all")

            assert "tasks" in result
            assert len(result["tasks"]) == 0
            assert "message" in result
        finally:
            tools_module.engine = original_engine

    def test_list_tasks_invalid_status(self, session: Session, user_id: str):
        """Test listing tasks with invalid status"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = list_tasks(user_id, "invalid")

            assert "error" in result
        finally:
            tools_module.engine = original_engine


class TestAddTask:
    """Tests for add_task tool"""

    def test_add_task(self, session: Session, user_id: str):
        """Test adding a task with title only"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = add_task(user_id, "Buy groceries")

            assert result["success"] is True
            assert result["task"]["title"] == "Buy groceries"
            assert "message" in result
        finally:
            tools_module.engine = original_engine

    def test_add_task_with_description(self, session: Session, user_id: str):
        """Test adding a task with title and description"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = add_task(
                user_id,
                "Review PR",
                "Check the authentication changes"
            )

            assert result["success"] is True
            assert result["task"]["title"] == "Review PR"
            assert result["task"]["description"] == "Check the authentication changes"
        finally:
            tools_module.engine = original_engine

    def test_add_task_empty_title(self, session: Session, user_id: str):
        """Test adding a task with empty title fails"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = add_task(user_id, "")

            assert "error" in result
        finally:
            tools_module.engine = original_engine


class TestCompleteTask:
    """Tests for complete_task tool"""

    def test_complete_task(self, session: Session, user_id: str, sample_task):
        """Test completing a task"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = complete_task(user_id, sample_task.id)

            assert result["success"] is True
            assert "marked as complete" in result["message"]
        finally:
            tools_module.engine = original_engine

    def test_complete_task_not_found(self, session: Session, user_id: str):
        """Test completing a non-existent task"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = complete_task(user_id, str(uuid4()))

            assert "error" in result
            assert "No matching task found" in result["error"]
        finally:
            tools_module.engine = original_engine

    def test_complete_task_wrong_user(self, session: Session, sample_task):
        """Test completing another user's task fails"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = complete_task(str(uuid4()), sample_task.id)

            assert "error" in result
            assert "No matching task found" in result["error"]
        finally:
            tools_module.engine = original_engine


class TestUpdateTask:
    """Tests for update_task tool"""

    def test_update_task_title(self, session: Session, user_id: str, sample_task):
        """Test updating task title"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = update_task(user_id, sample_task.id, title="Updated Title")

            assert result["success"] is True
            assert result["task"]["title"] == "Updated Title"
        finally:
            tools_module.engine = original_engine

    def test_update_task_description(self, session: Session, user_id: str, sample_task):
        """Test updating task description"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = update_task(
                user_id,
                sample_task.id,
                description="Updated description"
            )

            assert result["success"] is True
            assert result["task"]["description"] == "Updated description"
        finally:
            tools_module.engine = original_engine

    def test_update_task_not_found(self, session: Session, user_id: str):
        """Test updating a non-existent task"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = update_task(user_id, str(uuid4()), title="New Title")

            assert "error" in result
            assert "No matching task found" in result["error"]
        finally:
            tools_module.engine = original_engine

    def test_update_task_no_fields(self, session: Session, user_id: str, sample_task):
        """Test updating with no fields provided"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = update_task(user_id, sample_task.id)

            assert "error" in result
            assert "No fields provided" in result["error"]
        finally:
            tools_module.engine = original_engine


class TestDeleteTask:
    """Tests for delete_task tool"""

    def test_delete_task(self, session: Session, user_id: str, sample_task):
        """Test deleting a task"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = delete_task(user_id, sample_task.id)

            assert result["success"] is True
            assert "deleted" in result["message"]
        finally:
            tools_module.engine = original_engine

    def test_delete_task_not_found(self, session: Session, user_id: str):
        """Test deleting a non-existent task"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = delete_task(user_id, str(uuid4()))

            assert "error" in result
            assert "No matching task found" in result["error"]
        finally:
            tools_module.engine = original_engine

    def test_delete_task_wrong_user(self, session: Session, sample_task):
        """Test deleting another user's task fails"""
        import app.mcp.tools as tools_module
        original_engine = tools_module.engine
        tools_module.engine = session.get_bind()

        try:
            result = delete_task(str(uuid4()), sample_task.id)

            assert "error" in result
            assert "No matching task found" in result["error"]
        finally:
            tools_module.engine = original_engine
