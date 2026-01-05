# Skill: CreateTask

## Purpose
Instantiate a new todo task with provided attributes.

## When to Use
Invoke this skill when the user wants to create, add, or make a new task/todo item.

## Input Contract
```json
{
  "title": "string (required, 1-500 chars)",
  "description": "string (optional, max 5000 chars)",
  "due_date": "ISO8601 datetime (optional)",
  "priority": "integer 1-5 (optional, default 3)",
  "tags": "string[] (optional)"
}
```

## Output Contract
```json
{
  "task_id": "string",
  "created_at": "ISO8601 datetime",
  "title": "string",
  "status": "pending"
}
```

## Validation Rules
- Title must not be empty or whitespace-only
- Title must be between 1-500 characters
- Due date must be in the future if provided
- Priority must be integer between 1 and 5 inclusive
- Tags must be non-empty strings if provided

## Side Effects
- Emits `TaskCreated` domain event
- Persists task to storage

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | In-memory dict storage |
| Phase II | SQLModel/Neon persistence |
| Phase III | Same, invoked via chat |
| Phase IV | Kubernetes-deployed persistence |
| Phase V | Event published to Kafka |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Create a task to buy groceries due tomorrow with high priority
Parsed: { title: "Buy groceries", due_date: "2024-01-02T23:59:59Z", priority: 1 }
```

## Error Handling
- Empty title → Reject with "Title is required"
- Past due date → Reject with "Due date must be in the future"
- Invalid priority → Reject with "Priority must be between 1 and 5"
