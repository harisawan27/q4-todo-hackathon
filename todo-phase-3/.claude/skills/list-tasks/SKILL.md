# Skill: ListTasks

## Purpose
Retrieve tasks matching specified criteria.

## When to Use
Invoke this skill when the user wants to list, show, display, view, or get tasks.

## Input Contract
```json
{
  "filters": {
    "status": "pending | completed | all (optional)",
    "priority": "integer | integer[] (optional)",
    "tags": "string[] (optional)",
    "due_before": "ISO8601 datetime (optional)",
    "due_after": "ISO8601 datetime (optional)",
    "search": "string (optional)"
  },
  "pagination": {
    "offset": "integer (optional, default 0)",
    "limit": "integer (optional, default 50, max 200)"
  },
  "sort": {
    "field": "string (optional)",
    "direction": "asc | desc (optional)"
  }
}
```

## Output Contract
```json
{
  "tasks": "Task[]",
  "total_count": "integer",
  "offset": "integer",
  "limit": "integer",
  "has_more": "boolean"
}
```

## Validation Rules
- Limit must not exceed 200
- Offset must be non-negative
- Sort field must be a valid task property (title, due_date, priority, created_at, status)
- Status filter must be valid enum value

## Side Effects
- None (read-only operation)

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | In-memory filter/sort |
| Phase II | SQL query generation |
| Phase III | Same |
| Phase IV | Same |
| Phase V | Read from materialized view |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Show all pending tasks
Parsed: { filters: { status: "pending" } }

User: List high priority tasks due this week
Parsed: { filters: { priority: [1, 2], due_before: "2024-01-07T23:59:59Z" } }

User: Show completed tasks tagged with "work"
Parsed: { filters: { status: "completed", tags: ["work"] } }
```

## Error Handling
- Invalid sort field → Reject with "Invalid sort field: {field}"
- Limit exceeds max → Reject with "Limit cannot exceed 200"
- Negative offset → Reject with "Offset must be non-negative"
