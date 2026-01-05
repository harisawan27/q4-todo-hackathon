# Intelligence Layer Index

## Skills Directory

### Core CRUD Skills
- **create-task/** - Create new todo tasks
- **update-task/** - Modify existing tasks
- **delete-task/** - Remove tasks (soft/hard delete)
- **list-tasks/** - Query and filter tasks

### State Management Skills
- **toggle-task/** - Toggle completion status

### Enhancement Skills
- **reschedule-task/** - Change due dates
- **set-priority/** - Set priority levels (1-5)
- **manage-tags/** - Add/remove/replace tags

## Agents Directory

### Input Processing
- **intent-resolution/** - Parse raw input → structured requests

### Validation Layer
- **spec-governance/** - Validate against specifications

### Business Logic
- **todo-domain/** - Enforce domain rules, emit events

### Execution Layer
- **execution-planner/** - Orchestrate multi-step operations

### Infrastructure Layer
- **infrastructure-adapter/** - Abstract storage and messaging

## Pipeline Order

```
1. intent-resolution
2. spec-governance
3. todo-domain
4. execution-planner
5. infrastructure-adapter
```

## Quick Reference

### Skill Contracts Summary

| Skill | Required Input | Key Output |
|-------|---------------|------------|
| create-task | title | task_id, status |
| update-task | task_id, updates{} | changed_fields |
| delete-task | task_id | deletion_type |
| list-tasks | (optional filters) | tasks[], total_count |
| toggle-task | task_id | previous_status, new_status |
| reschedule-task | task_id, new_due_date | previous_due_date |
| set-priority | task_id, priority (1-5) | previous_priority |
| manage-tags | task_id, operation, tags[] | previous_tags, new_tags |

### Domain Events

| Event | Emitted By |
|-------|------------|
| TaskCreated | create-task |
| TaskUpdated | update-task |
| TaskDeleted | delete-task |
| TaskCompleted | toggle-task |
| TaskReopened | toggle-task |
| TaskRescheduled | reschedule-task |
| TaskPriorityChanged | set-priority |
| TaskTagsModified | manage-tags |

### Priority Mapping

| Value | Meaning | Keywords |
|-------|---------|----------|
| 1 | Critical | critical, urgent, highest, p1 |
| 2 | High | high, important, p2 |
| 3 | Medium | medium, normal, default, p3 |
| 4 | Low | low, minor, p4 |
| 5 | Lowest | lowest, trivial, p5 |
