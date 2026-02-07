# Data Model: Cloud-Native Event-Driven Task System

**Branch**: `002-cloud-native-event-driven` | **Date**: 2026-02-06
**Prereq**: research.md (R1 — PostgreSQL v2 index-key pattern)

---

## Storage Strategy

All entities are stored via the **Dapr State Management API** backed by PostgreSQL v2. There are no direct database tables, no ORM models, and no SQL queries in application code (Constitution III). Entities are serialized as JSON and stored as bytea blobs with Dapr-managed keys.

---

## 1. Task

**Owner Service**: chat-api
**State Key**: `task||{task-id}` → stored as `chat-api||task||{task-id}`
**Index Key**: `task-index||{user-id}` → stored as `chat-api||task-index||{user-id}`

```python
from pydantic import BaseModel, Field
from datetime import datetime, date, time
from enum import Enum
from typing import Optional
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.PENDING
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    tags: list[str] = Field(default_factory=list, max_length=10)
    recurrence_rule_id: Optional[str] = None
    parent_task_id: Optional[str] = None       # For recurring instances
    instance_number: Optional[int] = None       # Sequence for recurring
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    etag: Optional[str] = None                  # Populated from Dapr response header

class TaskCreate(BaseModel):
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    tags: list[str] = Field(default_factory=list)
    recurrence_rule: Optional["RecurrenceRuleCreate"] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    tags: Optional[list[str]] = None
    status: Optional[TaskStatus] = None

class TaskIndex(BaseModel):
    """Index of task IDs for a user. Stored at task-index||{user-id}."""
    user_id: str
    task_ids: list[str] = Field(default_factory=list)
```

### State Operations

| Operation | Dapr API Call | Key(s) | Notes |
|-----------|--------------|--------|-------|
| Create task | Transaction: upsert task + upsert index | `task||{id}`, `task-index||{user-id}` | Atomic via transaction |
| Get task | GET state | `task||{id}` | Returns ETag in header |
| List user tasks | GET index → Bulk GET | `task-index||{user-id}` → `task||{id1}`, `task||{id2}`, ... | Two-step lookup |
| Update task | Save state with ETag | `task||{id}` | 409 on ETag mismatch |
| Delete task | Transaction: delete task + update index | `task||{id}`, `task-index||{user-id}` | Remove ID from index |
| Complete task | Save state with ETag | `task||{id}` | Set status=completed, completed_at |

---

## 2. Recurrence Rule

**Owner Service**: recurring-engine
**State Key**: `recurrence-rule||{rule-id}` → stored as `recurring-engine||recurrence-rule||{rule-id}`
**Index Key**: `recurrence-index||{task-id}` → stored as `recurring-engine||recurrence-index||{task-id}`

```python
class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    WEEKDAY = "weekday"      # Mon-Fri
    MONTHLY = "monthly"
    CUSTOM = "custom"         # Raw cron expression

class RecurrenceEndCondition(str, Enum):
    NEVER = "never"
    COUNT = "count"
    DATE = "date"

class RecurrenceRule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str                                # Original/parent task ID
    user_id: str
    frequency: RecurrenceFrequency
    interval: int = 1                           # Every N (days/weeks/months)
    days_of_week: Optional[list[int]] = None    # 0=Mon, 6=Sun (for weekly)
    day_of_month: Optional[int] = None          # For monthly
    time_of_day: str = "09:00"                  # HH:MM format
    timezone: str = "UTC"
    cron_expression: Optional[str] = None       # For CUSTOM frequency
    end_condition: RecurrenceEndCondition = RecurrenceEndCondition.NEVER
    end_count: Optional[int] = None             # Max instances if COUNT
    end_date: Optional[date] = None             # End date if DATE
    instances_generated: int = 0                # Counter for tracking
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    job_name: Optional[str] = None              # Dapr Jobs API job name

class RecurrenceRuleCreate(BaseModel):
    frequency: RecurrenceFrequency
    interval: int = 1
    days_of_week: Optional[list[int]] = None
    day_of_month: Optional[int] = None
    time_of_day: str = "09:00"
    timezone: str = "UTC"
    cron_expression: Optional[str] = None
    end_condition: RecurrenceEndCondition = RecurrenceEndCondition.NEVER
    end_count: Optional[int] = None
    end_date: Optional[date] = None
```

### Recurrence Validation Rules

- `DAILY`: No additional fields required. `interval` controls "every N days".
- `WEEKLY`: `days_of_week` required (at least one day). `interval` controls "every N weeks".
- `WEEKDAY`: Automatically Mon-Fri. `interval` not applicable (always 1).
- `MONTHLY`: `day_of_month` required (1-28 only; 29-31 rejected with error per FR-018).
- `CUSTOM`: `cron_expression` required (validated against standard 5-field cron).

### State Transitions

```
Created (is_active=true) → Cancelled (is_active=false)
                          → End condition met (is_active=false)
```

---

## 3. Reminder

**Owner Service**: recurring-engine (registration), notification-service (delivery)
**State Key**: `reminder||{reminder-id}` → stored as `recurring-engine||reminder||{reminder-id}`
**Index Key**: `reminder-index||{task-id}` → stored as `recurring-engine||reminder-index||{task-id}`

```python
class ReminderStatus(str, Enum):
    SCHEDULED = "scheduled"
    FIRED = "fired"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ReminderLevel(str, Enum):
    DAY_BEFORE = "day-before"
    HOURS_12 = "12-hours-before"
    HOURS_6 = "6-hours-before"
    HOURS_3 = "3-hours-before"
    HOURS_1 = "1-hour-before"
    MINUTES_30 = "30-minutes-before"
    OVERDUE = "overdue"

class Reminder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    user_id: str
    trigger_time: datetime                      # When the reminder should fire
    reminder_level: ReminderLevel
    status: ReminderStatus = ReminderStatus.SCHEDULED
    notification_channel: str = "browser-push"
    job_name: Optional[str] = None              # Dapr Jobs API job name
    delivered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Default Reminder Schedule (for due-date tasks)

When a task is created with a `due_date`, the recurring-engine schedules:
- **30 minutes before** due time (primary reminder)

Additional levels can be configured per user preference (future enhancement).

---

## 4. Task Event (Immutable)

**Transport**: Kafka `task-events` topic (CloudEvents envelope)
**Not stored in Dapr State** — events live in Kafka. Audit service consumes and persists.

```python
class TaskEventType(str, Enum):
    CREATED = "task-created"
    UPDATED = "task-updated"
    COMPLETED = "task-completed"
    DELETED = "task-deleted"
    RECURRENCE_GENERATED = "task-recurrence-generated"

class TaskEvent(BaseModel):
    """CloudEvents data payload for task-events topic."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: TaskEventType
    task_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict                                  # Event-specific payload (see plan.md §4.2)
```

### Event-Specific Data Payloads

| Event Type | `data` Fields |
|------------|---------------|
| `task-created` | `title`, `description`, `status`, `priority`, `dueDate`, `tags`, `recurrenceRule`, `etag` |
| `task-updated` | `before` (changed fields), `after` (changed fields), `changedFields[]`, `etag` |
| `task-completed` | `title`, `completedAt`, `hasRecurrence`, `etag` |
| `task-deleted` | `title`, `deletedAt` |
| `task-recurrence-generated` | `title`, `status`, `dueDate`, `recurrenceRule`, `instanceNumber`, `parentTaskId`, `etag` |

---

## 5. Notification

**Owner Service**: notification-service
**State Key**: `notification||{notification-id}` → stored as `notification-service||notification||{notification-id}`
**Index Key**: `notification-index||{user-id}` → stored as `notification-service||notification-index||{user-id}`

```python
class NotificationType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"
    DEADLINE_APPROACHING = "deadline_approaching"
    DEADLINE_PASSED = "deadline_passed"
    RECURRENCE_GENERATED = "recurrence_generated"
    SYSTEM = "system"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    type: NotificationType
    task_id: Optional[str] = None
    reminder_level: Optional[str] = None
    read: bool = False
    delivered: bool = False
    delivered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

## 6. Push Subscription

**Owner Service**: notification-service
**State Key**: `push-subscription||{subscription-id}` → stored as `notification-service||push-subscription||{subscription-id}`
**Index Key**: `push-sub-index||{user-id}` → stored as `notification-service||push-sub-index||{user-id}`

```python
class PushSubscription(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    endpoint: str                               # Web Push endpoint URL
    auth: str                                   # Web Push auth key
    p256dh: str                                 # Web Push P-256 ECDH key
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

## 7. Conversation Context

**Owner Service**: chat-api
**State Key**: `conversation||{conversation-id}` → stored as `chat-api||conversation||{conversation-id}`
**Index Key**: `conversation-index||{user-id}` → stored as `chat-api||conversation-index||{user-id}`
**TTL**: 4 hours (active sessions expire automatically)

```python
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ConversationContext(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    messages: list[Message] = Field(default_factory=list, max_length=50)
    current_intent: Optional[str] = None
    extracted_entities: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

### Message Trimming Strategy

- Max 50 messages per conversation.
- When limit reached, remove oldest messages (FIFO).
- System summary of trimmed context preserved as first message.

---

## 8. Audit Record (P3)

**Owner Service**: Audit consumer (may be part of chat-api or a 4th service)
**State Key**: `audit||{audit-id}` → stored as `{service}||audit||{audit-id}`
**Index Key**: `audit-index||{task-id}` → stored as `{service}||audit-index||{task-id}`

```python
class AuditAction(str, Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"
    RECURRENCE_GENERATED = "RECURRENCE_GENERATED"

class AuditRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str                               # Source event from task-events topic
    task_id: str
    user_id: str
    action: AuditAction
    timestamp: datetime
    change_summary: str                         # Human-readable change description
    before_state: Optional[dict] = None         # Snapshot before change
    after_state: Optional[dict] = None          # Snapshot after change
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

---

## Entity Relationship Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Dapr State Store                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  chat-api owns:                                                     │
│  ┌──────────────┐    1:N    ┌─────────────────────┐                │
│  │     Task      │◄────────│  ConversationContext  │                │
│  │  (task||{id}) │          │ (conversation||{id}) │                │
│  └──────┬───────┘          └─────────────────────┘                 │
│         │                                                           │
│         │ task-index||{user-id} → [task-id, ...]                   │
│         │ conversation-index||{user-id} → [conv-id, ...]           │
│                                                                     │
│  recurring-engine owns:                                             │
│  ┌──────────────────┐    1:1    ┌────────────┐                     │
│  │  RecurrenceRule   │◄────────│   Reminder   │                     │
│  │(recurrence-rule|| │          │(reminder||  │                     │
│  │      {id})        │          │   {id})     │                     │
│  └──────────────────┘          └────────────┘                      │
│         │                                                           │
│         │ Links to Task via task_id field                           │
│                                                                     │
│  notification-service owns:                                         │
│  ┌──────────────────┐    1:N    ┌──────────────────┐               │
│  │   Notification    │          │ PushSubscription   │              │
│  │(notification||{id}│          │(push-subscription||│              │
│  │                   │          │       {id})        │              │
│  └──────────────────┘          └──────────────────┘                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     Kafka Topics (Dapr Pub/Sub)                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  task-events:    TaskEvent (immutable, all task state changes)      │
│  reminders:      ReminderFired events (triggers notifications)      │
│  task-updates:   TaskUpdateBroadcast (real-time client updates)     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Migration from Phase 2 Models

| Phase 2 (SQLModel) | Phase 5 (Pydantic + Dapr State) | Changes |
|---------------------|--------------------------------|---------|
| `Task` (SQLModel, id=UUID) | `Task` (Pydantic, id=str UUID) | Removed SQLModel base; added recurrence_rule_id, parent_task_id, instance_number |
| `Notification` (SQLModel) | `Notification` (Pydantic) | Moved to notification-service; added delivered field |
| `Conversation` (SQLModel) | `ConversationContext` (Pydantic) | Merged messages inline; added intent/entity extraction; TTL |
| `Message` (SQLModel) | `Message` (nested in ConversationContext) | Inlined into conversation; max 50 |
| `FcmToken` (SQLModel) | Dropped | Replaced by PushSubscription (browser Push API only) |
| `PushSubscription` (SQLModel) | `PushSubscription` (Pydantic) | Moved to notification-service |
| N/A | `RecurrenceRule` | New entity for recurring task support |
| N/A | `Reminder` | New entity for due-date reminders |
| N/A | `AuditRecord` | New entity for task change audit trail (P3) |
