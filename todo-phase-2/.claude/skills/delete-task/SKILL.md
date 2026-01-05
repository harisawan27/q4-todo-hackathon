# Skill: DeleteTask

## Purpose
Remove a task from active state.

## When to Use
Invoke this skill when the user wants to delete, remove, or discard a task.

## Input Contract
```json
{
  "task_id": "string (required)",
  "hard_delete": "boolean (optional, default false)"
}
```

## Output Contract
```json
{
  "task_id": "string",
  "deleted_at": "ISO8601 datetime",
  "deletion_type": "soft | hard"
}
```

## Validation Rules
- Task must exist
- Hard delete requires explicit confirmation
- Soft-deleted tasks can be restored; hard-deleted cannot
- Cannot delete already hard-deleted tasks

## Side Effects
- Emits `TaskDeleted` domain event
- Soft delete: marks status as deleted
- Hard delete: removes from storage permanently

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | Remove from dict or mark deleted |
| Phase II | Soft delete via status column |
| Phase III | Same |
| Phase IV | Same |
| Phase V | Tombstone event for Kafka consumers |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Delete task 5
Parsed: { task_id: "5", hard_delete: false }

User: Permanently delete task 5
Parsed: { task_id: "5", hard_delete: true }
```

## Error Handling
- Task not found → Reject with "Task {id} not found"
- Already deleted → Reject with "Task already deleted"
- Hard delete without confirmation → Request confirmation first
