# Skill: RescheduleTask

## Purpose
Change the due date of an existing task.

## When to Use
Invoke this skill when the user wants to:
- Change a task's due date
- Postpone/defer a task
- Move a task to a different date
- Set a new deadline

## Input Contract
```json
{
  "task_id": "string (required)",
  "new_due_date": "ISO8601 datetime (required)",
  "reason": "string (optional, for audit)"
}
```

## Output Contract
```json
{
  "task_id": "string",
  "previous_due_date": "ISO8601 datetime | null",
  "new_due_date": "ISO8601 datetime",
  "rescheduled_at": "ISO8601 datetime",
  "reschedule_count": "integer"
}
```

## Validation Rules
- Task must exist
- New due date must be valid datetime
- New due date in past triggers warning (not error)
- Cannot reschedule completed tasks without reopening first
- Cannot reschedule deleted tasks

## Side Effects
- Emits `TaskRescheduled` domain event
- Increments reschedule counter for tracking
- Stores reason if provided for audit trail

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | Date field update in dict |
| Phase II | Update with audit trail in DB |
| Phase III | Same, AI may suggest optimal dates |
| Phase IV | Same |
| Phase V | Event with causation tracking |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Move task 3 to next Monday
Parsed: { task_id: "3", new_due_date: "2024-01-08T23:59:59Z" }

User: Postpone the grocery task by 2 days
Parsed: { task_id: "<resolved_id>", new_due_date: "<calculated_date>" }

User: Reschedule task 5 to tomorrow because I'm busy today
Parsed: { task_id: "5", new_due_date: "<tomorrow>", reason: "busy today" }
```

## Error Handling
- Task not found → Reject with "Task {id} not found"
- Task completed → Reject with "Cannot reschedule completed task. Reopen it first."
- Task deleted → Reject with "Cannot reschedule deleted task"
- Invalid date format → Reject with "Invalid date format"
