---
id: 009
title: Create Phase 2 Dapr Clients and Domain Models
stage: green
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: developer
command: create files
labels: ["dapr-client", "domain-models", "phase-2", "httpx", "pydantic"]
links:
  spec: specs/002-cloud-native-event-driven/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - services/chat-api/app/dapr_client.py
  - services/notification-service/app/dapr_client.py
  - services/recurring-engine/app/dapr_client.py
  - services/chat-api/app/models/__init__.py
  - services/chat-api/app/models/task.py
  - services/chat-api/app/models/events.py
  - services/chat-api/app/models/conversation.py
  - services/recurring-engine/app/models/__init__.py
  - services/recurring-engine/app/models/recurrence.py
  - services/recurring-engine/app/models/job.py
  - services/notification-service/app/models/__init__.py
  - services/notification-service/app/models/notification.py
  - services/notification-service/app/models/subscription.py
tests:
  - none
---

## Prompt

Create the following files in F:\q4-todo-hackathon\todo-phase-5\. These are Phase 2 foundational files. Write complete, production-quality Python code.

All services use the same Dapr HTTP client pattern via httpx. Key pattern: app-id auto-prefixes keys, so we save key "task||{id}" and Dapr stores it as "chat-api||task||{id}".

13 files total covering:
- T020: chat-api dapr_client.py (port 3500)
- T021: notification-service dapr_client.py (port 3501)
- T022: recurring-engine dapr_client.py (port 3502, with Jobs API)
- T023: Task, TaskCreate, TaskUpdate, TaskIndex, TaskStatus, TaskPriority models
- T024: TaskEvent, TaskEventType, TaskUpdateBroadcast event models
- T025: ConversationContext, Message, MessageRole conversation models
- T026: RecurrenceRule, RecurrenceRuleCreate, RecurrenceFrequency, RecurrenceEndCondition models
- T027: JobRegistration, JobCallback job models
- T028: Notification, NotificationType models
- T029: PushSubscription, PushSubscriptionIndex models
- Three __init__.py files re-exporting all model classes

## Response snapshot

Created all 13 files successfully across the three microservices:

**Dapr HTTP Client Wrappers (3 files):**
- chat-api (port 3500): publish_event, get_state, save_state, delete_state, bulk_get_state, transact_state, get_secret
- notification-service (port 3501): same base API set
- recurring-engine (port 3502): base API set + register_job, delete_job, get_job (Dapr Jobs API alpha1)

**Domain Models (7 files):**
- task.py: Task, TaskCreate, TaskUpdate, TaskIndex with TaskStatus/TaskPriority enums
- events.py: TaskEvent, TaskUpdateBroadcast with TaskEventType enum
- conversation.py: ConversationContext with Message/MessageRole, 50-message sliding window
- recurrence.py: RecurrenceRule, RecurrenceRuleCreate with frequency/end-condition enums
- job.py: JobRegistration (schedule, repeats, due_time, ttl, data) and JobCallback
- notification.py: Notification with NotificationType enum (7 types)
- subscription.py: PushSubscription (Web Push fields) and PushSubscriptionIndex

**Module Init Files (3 files):**
- chat-api/app/models/__init__.py: re-exports all task, event, and conversation models
- recurring-engine/app/models/__init__.py: re-exports recurrence and job models
- notification-service/app/models/__init__.py: re-exports notification and subscription models

## Outcome

- Impact: Phase 2 foundational layer complete -- all Dapr client wrappers and Pydantic domain models for three microservices
- Tests: none (models are data-only; Dapr clients require sidecar for integration testing)
- Files: 13 new files created
- Next prompts: Implement task CRUD service layer (T030), event handlers/subscribers, recurring engine logic
- Reflection: Clean separation of concerns across services; each service gets its own Dapr port and only the recurring-engine has Jobs API methods

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add unit tests for model serialization/validation
