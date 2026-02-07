# Skill: SetPriority

## Purpose
Assign or change the priority level of a task.

## When to Use
Invoke this skill when the user wants to:
- Set a task's priority
- Change priority level
- Mark as high/medium/low priority
- Prioritize or deprioritize a task

## Input Contract
```json
{
  "task_id": "string (required)",
  "priority": "integer 1-5 (required)"
}
```

### Priority Levels
| Value | Meaning |
|-------|---------|
| 1 | Critical / Highest |
| 2 | High |
| 3 | Medium (default) |
| 4 | Low |
| 5 | Lowest |

## Output Contract
```json
{
  "task_id": "string",
  "previous_priority": "integer",
  "new_priority": "integer",
  "updated_at": "ISO8601 datetime"
}
```

## Validation Rules
- Task must exist
- Priority must be integer between 1 and 5 inclusive
- Cannot set priority on deleted tasks

## Side Effects
- Emits `TaskPriorityChanged` domain event

## Phase Evolution
| Phase | Implementation |
|-------|----------------|
| Phase I | Integer field update in dict |
| Phase II | Column update in DB |
| Phase III | AI may suggest priority based on content |
| Phase IV | Same |
| Phase V | Priority affects event routing/ordering |

**Contract remains unchanged across all phases.**

## Example Usage
```
User: Set task 3 to high priority
Parsed: { task_id: "3", priority: 2 }

User: Make the grocery task critical
Parsed: { task_id: "<resolved_id>", priority: 1 }

User: Lower priority of task 5
Parsed: { task_id: "5", priority: <current + 1, max 5> }

User: Mark task 2 as low priority
Parsed: { task_id: "2", priority: 4 }
```

## Natural Language Mapping
| User Says | Priority Value |
|-----------|---------------|
| critical, urgent, highest, p1 | 1 |
| high, important, p2 | 2 |
| medium, normal, default, p3 | 3 |
| low, minor, p4 | 4 |
| lowest, trivial, p5 | 5 |

## Error Handling
- Task not found → Reject with "Task {id} not found"
- Invalid priority → Reject with "Priority must be between 1 and 5"
- Task deleted → Reject with "Cannot set priority on deleted task"
