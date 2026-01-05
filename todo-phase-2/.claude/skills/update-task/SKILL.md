# Skill: UpdateTask

## Purpose
Modify mutable attributes of an existing task.

## When to Use
Invoke this skill when the user wants to edit, modify, change, or update an existing task's properties.

## Input Contract
```json
{
  "task_id": "string (required)",
  "updates": {
    "title": "string (optional)",
    "description": "string (optional)",
    "due_date": "ISO8601 datetime (optional)",
    "priority": "integer 1-5 (optional)",
    "tags": "string[] (optional)"
  }
}
```

## Output Contract
```json
{
  "task_id": "string",
  "updated_at": "ISO8601 datetime",
  "changed_fields": "string[]",
  "previous_values": "object",
  "new_values": "object"
}
```

## Validation Rules
- Task must exist
- At least one field must be updated
- New values must pass same validation as CreateTask
- Cannot update deleted tasks
- Title if provided must be 1-500 characters
- Priority if provided must be 1-5

## Side Effects
- Emits `TaskUpdated` domain event with changelog
- Persists changes to storage

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | Direct dict mutation |
| Phase II | SQLModel update |
| Phase III | Same |
| Phase IV | Same with pod-local state consideration |
| Phase V | CQRS write to event store |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Change task 3's title to "Buy organic groceries"
Parsed: { task_id: "3", updates: { title: "Buy organic groceries" } }
```

## Error Handling
- Task not found → Reject with "Task {id} not found"
- No updates provided → Reject with "At least one field must be updated"
- Task deleted → Reject with "Cannot update deleted task"
