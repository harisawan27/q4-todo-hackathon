# Skill: ManageTags

## Purpose
Add, remove, or replace tags on a task.

## When to Use
Invoke this skill when the user wants to:
- Add tags/labels to a task
- Remove tags from a task
- Replace all tags on a task
- Label or categorize a task

## Input Contract
```json
{
  "task_id": "string (required)",
  "operation": "add | remove | replace (required)",
  "tags": "string[] (required, non-empty)"
}
```

## Output Contract
```json
{
  "task_id": "string",
  "previous_tags": "string[]",
  "new_tags": "string[]",
  "operation_performed": "string",
  "updated_at": "ISO8601 datetime"
}
```

## Validation Rules
- Task must exist
- Tags must be non-empty strings
- Tags are case-insensitive (stored lowercase)
- Tags cannot contain spaces (use hyphens)
- Maximum 20 tags per task
- Each tag maximum 50 characters

## Operation Behavior
| Operation | Behavior |
|-----------|----------|
| add | Appends tags, ignores duplicates |
| remove | Removes specified tags, ignores non-existent |
| replace | Overwrites all tags completely |

## Side Effects
- Emits `TaskTagsModified` domain event

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | List manipulation in dict |
| Phase II | Junction table or array column |
| Phase III | AI may suggest tags based on content |
| Phase IV | Same |
| Phase V | Tags enable event routing rules |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Add "work" tag to task 3
Parsed: { task_id: "3", operation: "add", tags: ["work"] }

User: Tag the grocery task with "shopping" and "weekend"
Parsed: { task_id: "<resolved_id>", operation: "add", tags: ["shopping", "weekend"] }

User: Remove the "urgent" tag from task 5
Parsed: { task_id: "5", operation: "remove", tags: ["urgent"] }

User: Replace tags on task 2 with "home" and "maintenance"
Parsed: { task_id: "2", operation: "replace", tags: ["home", "maintenance"] }
```

## Error Handling
- Task not found → Reject with "Task {id} not found"
- Empty tags array → Reject with "At least one tag is required"
- Invalid tag format → Reject with "Tags cannot contain spaces"
- Too many tags → Reject with "Maximum 20 tags per task"
- Task deleted → Reject with "Cannot modify tags on deleted task"
