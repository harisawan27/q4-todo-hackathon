# Skill: ToggleTaskCompletion

## Purpose
Switch task between pending and completed states.

## When to Use
Invoke this skill when the user wants to:
- Mark a task as done/complete/finished
- Mark a task as incomplete/undone/pending
- Toggle a task's completion status
- Check/uncheck a task

## Input Contract
```json
{
  "task_id": "string (required)"
}
```

## Output Contract
```json
{
  "task_id": "string",
  "previous_status": "pending | completed",
  "new_status": "pending | completed",
  "toggled_at": "ISO8601 datetime"
}
```

## Validation Rules
- Task must exist
- Task must not be deleted

## Side Effects
- Emits `TaskCompleted` or `TaskReopened` domain event
- Updates completion timestamp
- If completing: sets completed_at timestamp
- If reopening: clears completed_at timestamp

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | Boolean flip in dict |
| Phase II | Status column update with timestamp |
| Phase III | Same |
| Phase IV | Same |
| Phase V | Event sourced state change |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Mark task 3 as done
Parsed: { task_id: "3" }

User: Complete the grocery task
Parsed: { task_id: "<resolved_id>" }

User: Reopen task 5
Parsed: { task_id: "5" }

User: Uncheck task 2
Parsed: { task_id: "2" }
```

## Error Handling
- Task not found → Reject with "Task {id} not found"
- Task deleted → Reject with "Cannot toggle deleted task"
