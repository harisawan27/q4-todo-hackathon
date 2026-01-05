# Data Model: Phase II Multi-User Web Todo Application

**Branch**: `001-multi-user-web` | **Date**: 2026-01-05

## Entity Overview

```
┌─────────────────┐          ┌─────────────────┐
│      User       │          │      Task       │
│─────────────────│          │─────────────────│
│ id (PK)         │──────────│ id (PK)         │
│ email           │     1:N  │ user_id (FK)    │
│ name            │          │ title           │
│ created_at      │          │ completed       │
│ updated_at      │          │ created_at      │
└─────────────────┘          │ updated_at      │
                             └─────────────────┘
```

## Entity Definitions

### User (Managed by Better-Auth)

**Note**: User entity is managed by Better-Auth in the frontend. Backend only references `user_id` from JWT claims.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID (string) | Primary Key | Better-Auth generated identifier |
| email | string | Unique, Not Null | User email address |
| name | string | Optional | Display name |
| created_at | timestamp | Not Null, Default: now() | Account creation time |
| updated_at | timestamp | Not Null, Auto-update | Last modification time |

**Source of Truth**: Better-Auth session/database

---

### Task

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID (string) | Primary Key, Default: uuid4 | Task unique identifier |
| user_id | UUID (string) | Foreign Key (users.id), Not Null, Indexed | Owner reference from JWT sub claim |
| title | string(500) | Not Null, Min 1 char | Task description |
| completed | boolean | Not Null, Default: false | Completion status |
| created_at | timestamp | Not Null, Default: now() | Task creation time |
| updated_at | timestamp | Not Null, Auto-update | Last modification time |

**Constraints**:
- Title must be 1-500 characters
- user_id is always set from JWT, never from request body
- All queries MUST filter by user_id

---

## SQLModel Definitions

### Backend Models (Python)

```python
# backend/app/models/task.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from uuid import uuid4

class TaskBase(SQLModel):
    """Base task fields for create/update operations"""
    title: str = Field(min_length=1, max_length=500)

class Task(TaskBase, table=True):
    """Database task model"""
    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True, foreign_key="users.id")
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TaskCreate(TaskBase):
    """Request schema for creating a task"""
    pass

class TaskUpdate(SQLModel):
    """Request schema for updating a task"""
    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    completed: Optional[bool] = None

class TaskRead(TaskBase):
    """Response schema for reading a task"""
    id: str
    user_id: str
    completed: bool
    created_at: datetime
    updated_at: datetime
```

---

## Relationships

### User → Task (One-to-Many)

- A User can have many Tasks
- A Task belongs to exactly one User
- Relationship enforced at query level, not ORM level (for security)
- No cascading deletes at ORM level (handled explicitly)

**Query Pattern**:
```python
# Always filter by user_id from JWT
select(Task).where(Task.user_id == current_user.user_id)
```

---

## State Transitions

### Task Completion State Machine

```
┌──────────────┐     toggle()     ┌──────────────┐
│  incomplete  │ ───────────────► │   complete   │
│ (default)    │ ◄─────────────── │              │
└──────────────┘     toggle()     └──────────────┘
```

**Rules**:
- New tasks start as `completed = false`
- Toggle operation flips the boolean
- No intermediate states

---

## Validation Rules

### Task Title
| Rule | Value | Error Code |
|------|-------|------------|
| Minimum length | 1 character | VALIDATION_ERROR |
| Maximum length | 500 characters | VALIDATION_ERROR |
| Empty after trim | Not allowed | VALIDATION_ERROR |

### User ID (from JWT)
| Rule | Description | Error Code |
|------|-------------|------------|
| Required | Must be present in JWT `sub` claim | UNAUTHORIZED |
| Format | Valid UUID string | UNAUTHORIZED |
| Ownership | Task.user_id must match JWT user_id for access | NOT_FOUND (intentional) |

**Security Note**: When a task is not found OR not owned by the user, return 404 NOT_FOUND to prevent enumeration attacks.

---

## Indexes

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| tasks | tasks_pkey | Primary | Task lookup |
| tasks | ix_tasks_user_id | B-tree | User task queries |
| tasks | ix_tasks_user_id_created_at | Composite | Ordered task lists |

**SQL**:
```sql
CREATE INDEX ix_tasks_user_id ON tasks (user_id);
CREATE INDEX ix_tasks_user_id_created_at ON tasks (user_id, created_at DESC);
```

---

## Migration Strategy

### Initial Schema (Migration 001)

```sql
-- 001_create_tasks_table.sql
CREATE TABLE tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(500) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
);

CREATE INDEX ix_tasks_user_id ON tasks (user_id);
CREATE INDEX ix_tasks_user_id_created_at ON tasks (user_id, created_at DESC);
```

**Note**: Foreign key to users table is omitted since Better-Auth manages users separately. The user_id is validated at the application layer via JWT verification.

---

## TypeScript Types (Frontend)

```typescript
// types/task.ts
export interface Task {
  id: string;
  user_id: string;
  title: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaskCreate {
  title: string;
}

export interface TaskUpdate {
  title?: string;
  completed?: boolean;
}
```

---

## Data Model Verification

| Requirement | Addressed |
|-------------|-----------|
| User identity from JWT | user_id from sub claim |
| Task ownership | user_id foreign key |
| Title validation | 1-500 chars, non-empty |
| Completion toggle | Boolean completed field |
| Audit timestamps | created_at, updated_at |
| Query optimization | Indexes on user_id |
| Tenant isolation | Query-level filtering enforced |
