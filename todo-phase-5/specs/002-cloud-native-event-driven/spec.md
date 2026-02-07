# Feature Specification: Cloud-Native Event-Driven Task System

**Feature Branch**: `002-cloud-native-event-driven`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Transition from Phase 2 (todo-phase-2) monolith to a Cloud-Native, event-driven system with conversational task management, recurring tasks, real-time updates, Kafka event bus, Dapr abstraction, notification engine, and audit trail."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversational Task Management via Chatbot (Priority: P1)

A user opens the chatbot interface (refactored from Phase 2) and interacts using natural language to create, update, query, and complete tasks. The chatbot interprets intent, performs the requested operation, and confirms the result in a conversational response. All task operations produce events that downstream services can consume.

**Why this priority**: This is the core user interaction surface. Without conversational task management, no other feature (recurring tasks, notifications, audit) has meaningful input. It delivers immediate value by preserving the Phase 2 chatbot experience while migrating to an event-driven backend.

**Independent Test**: Can be fully tested by sending natural language messages to the Chat API and verifying that tasks are created/updated/deleted in the state store and corresponding events are published to the event bus.

**Acceptance Scenarios**:

1. **Given** a user is authenticated and the chatbot is ready, **When** the user says "Create a task: Buy groceries", **Then** a new task is created in the state store, a `task-created` event is published, and the chatbot confirms "Task 'Buy groceries' created successfully."
2. **Given** a task "Buy groceries" exists, **When** the user says "Mark 'Buy groceries' as done", **Then** the task status is updated to completed, a `task-completed` event is published, and the chatbot confirms completion.
3. **Given** multiple tasks exist, **When** the user says "Show my tasks", **Then** the chatbot returns a formatted list of all active tasks with their status, due dates, and priorities.
4. **Given** a task "Buy groceries" exists, **When** the user says "Delete 'Buy groceries'", **Then** the task is removed, a `task-deleted` event is published, and the chatbot confirms deletion.
5. **Given** a task exists, **When** the user says "Update 'Buy groceries' to 'Buy organic groceries'", **Then** the task title is updated, a `task-updated` event is published, and the chatbot confirms the change.

---

### User Story 2 - Recurring Tasks and Due Dates (Priority: P2)

A user sets recurring schedules (e.g., "Remind me every Monday at 9 AM") and due dates on tasks through the chatbot. The system schedules jobs to trigger at the specified times. When a recurring task is completed, the system automatically generates the next instance based on the recurrence rule without user intervention.

**Why this priority**: Recurring tasks and due dates are the key differentiator from a simple todo list. They enable productivity workflows (weekly reviews, daily habits, deadline tracking) that drive user retention. They depend on P1 (task CRUD) being functional.

**Independent Test**: Can be tested by creating a recurring task, completing it, and verifying that the next instance is automatically generated with the correct future date. Due date tasks can be tested by setting a due date and verifying the scheduled reminder fires.

**Acceptance Scenarios**:

1. **Given** a user is in the chatbot, **When** the user says "Create a recurring task: Team standup every weekday at 9 AM", **Then** the task is created with a recurrence rule, a scheduled job is registered, and the chatbot confirms the recurring schedule.
2. **Given** a recurring task "Team standup" with a daily-weekday schedule exists, **When** the user completes today's instance, **Then** the system automatically creates the next instance for the next weekday at 9 AM and publishes a `task-recurrence-generated` event.
3. **Given** a user says "Set due date for 'Project proposal' to next Friday", **When** the system processes the request, **Then** the task is updated with the due date, and a reminder job is scheduled to fire before the deadline.
4. **Given** a recurring task exists, **When** the user says "Stop recurring for 'Team standup'", **Then** the recurrence rule is removed, the scheduled job is cancelled, and the chatbot confirms the change.

---

### User Story 3 - Real-Time Notifications and Cross-Client Updates (Priority: P2)

Users receive push notifications when reminders fire (due dates approaching, recurring task triggers). When any task changes, all connected clients see the update in real time without refreshing. The notification engine operates independently so that the Chat API remains functional even if notifications are unavailable.

**Why this priority**: Real-time awareness transforms the system from a passive record into an active assistant. It shares P2 priority with recurring tasks because notifications are the delivery mechanism for reminders. However, the Chat API must never depend on notification availability.

**Independent Test**: Can be tested by triggering a reminder event and verifying the notification is delivered to the user. Cross-client updates can be tested by modifying a task on one client and observing the change appear on another connected client.

**Acceptance Scenarios**:

1. **Given** a task has a due date of "today at 5 PM" and a reminder is scheduled for 30 minutes before, **When** the clock reaches 4:30 PM, **Then** the Notification Service delivers a notification to the user with the task details.
2. **Given** two clients are connected for the same user, **When** a task is created on Client A, **Then** Client B receives the update and displays the new task without a page refresh.
3. **Given** the Notification Service is down, **When** a user interacts with the Chat API to create or update tasks, **Then** the Chat API operates normally, task events are still published, and notifications are delivered when the Notification Service recovers.
4. **Given** a user has browser notifications enabled, **When** a reminder fires, **Then** the user receives a browser notification with the task name, due date, and a link to view the task.

---

### User Story 4 - Audit Trail for Task History (Priority: P3)

Every change to a task (creation, update, completion, deletion, recurrence generation) is logged by a dedicated Audit Service. Users can query the history of any task to see a chronological timeline of all changes, who made them, and when.

**Why this priority**: Audit trails are essential for accountability and debugging but do not affect core task management functionality. They consume events asynchronously and can be added after P1 and P2 features are stable.

**Independent Test**: Can be tested by performing several task operations and then querying the audit log to verify all changes are recorded with correct timestamps, action types, and before/after states.

**Acceptance Scenarios**:

1. **Given** a task "Buy groceries" is created, **When** the Audit Service receives the `task-created` event, **Then** an audit record is stored with the task details, timestamp, user ID, and action type "CREATED".
2. **Given** a task has been created, updated twice, and completed, **When** a user asks "Show history for 'Buy groceries'", **Then** the chatbot returns a chronological list of all four changes with timestamps and details.
3. **Given** the Audit Service is temporarily unavailable, **When** task events are published, **Then** the events are retained in the event bus and the Audit Service processes them upon recovery (no events are lost).

---

### Edge Cases

- What happens when a user creates a recurring task with an invalid schedule (e.g., "every 30th of February")? The system must reject the schedule with a clear error message explaining the issue.
- What happens when the state store is temporarily unreachable? The Chat API must return a graceful error and retry the operation, not crash or lose user context.
- What happens when two users attempt to modify the same task simultaneously? Optimistic locking (ETags) must prevent data loss; the second writer receives a conflict notification.
- What happens when a recurring task's next instance falls on a date in the past (e.g., service was down for days)? The system must generate only the next future instance, not backfill missed instances.
- What happens when a user sends an unrecognizable message to the chatbot? The chatbot must respond with a helpful clarification prompt rather than failing silently.
- What happens when the event bus is unavailable? The Chat API must still accept and store tasks locally; events must be published when the bus recovers.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow users to create, read, update, delete, and complete tasks through natural language conversation with the chatbot.
- **FR-002**: System MUST publish a domain event to the `task-events` topic for every task state change (create, update, delete, complete).
- **FR-003**: System MUST support recurring task schedules including daily, weekly, weekday-only, monthly, and custom cron-like patterns.
- **FR-004**: System MUST automatically generate the next instance of a recurring task when the current instance is completed.
- **FR-005**: System MUST allow users to set due dates on tasks and schedule reminder notifications relative to the due date.
- **FR-006**: System MUST deliver notifications to users when scheduled reminders fire, via a dedicated Notification Service that consumes from the `reminders` topic.
- **FR-007**: System MUST propagate task changes to all connected clients in real time via the `task-updates` topic.
- **FR-008**: System MUST log every task change (with before/after state, timestamp, user ID, and action type) through a dedicated Audit Service consuming from `task-events`.
- **FR-009**: Chat API MUST remain fully functional when the Notification Service or Audit Service is unavailable (resilience requirement).
- **FR-010**: System MUST store conversation context and task metadata using a Dapr-abstracted state store backed by PostgreSQL, with no direct database drivers in application code.
- **FR-011**: System MUST use the Dapr Jobs API for scheduling reminders and recurring task triggers (no cron polling, sleep timers, or OS cron).
- **FR-012**: System MUST use the Dapr Pub/Sub building block for all inter-service messaging via Kafka (no direct Kafka client libraries in application code).
- **FR-013**: All services MUST emit structured JSON logs to stdout with fields: timestamp, level, service, trace_id, message.
- **FR-014**: Application code MUST contain zero hardcoded connection strings for Kafka, PostgreSQL, or any external service; all infrastructure access MUST go through Dapr sidecars.
- **FR-015**: System MUST resolve credentials exclusively through the Dapr Secrets API (backed by Kubernetes Secrets), with `.env` files permitted only for local development.
- **FR-016**: System MUST deploy successfully to Minikube for local development and to a production-grade Kubernetes cluster (AKS/GKE/OKE).
- **FR-017**: System MUST handle concurrent task modifications using optimistic locking (ETags) to prevent data loss.
- **FR-018**: System MUST gracefully handle invalid recurrence schedules by returning clear error messages to the user.

### Key Entities

- **Task**: Represents a unit of work. Attributes: ID, title, description, status (pending/completed/deleted), due date, recurrence rule, creator, created timestamp, updated timestamp, ETag.
- **Recurrence Rule**: Defines the repeat pattern for a task. Attributes: frequency (daily/weekly/monthly/custom), interval, days of week, time of day, end condition (never/count/date).
- **Reminder**: A scheduled notification tied to a task's due date. Attributes: ID, task ID, trigger time, notification channel, delivery status.
- **Task Event**: An immutable record of a task state change. Attributes: event ID, event type (created/updated/deleted/completed/recurrence-generated), task ID, timestamp, user ID, before state, after state.
- **Audit Record**: A persistent log entry derived from task events. Attributes: ID, event ID, task ID, action type, timestamp, user ID, change summary.
- **Conversation Context**: Stores the current chatbot session state. Attributes: session ID, user ID, message history, current intent, extracted entities.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task through the chatbot in under 3 seconds end-to-end (from message sent to confirmation received).
- **SC-002**: When a recurring task is completed, the next instance appears within 5 seconds without user intervention.
- **SC-003**: Task change notifications are delivered to connected clients within 2 seconds of the originating event.
- **SC-004**: The system supports at least 100 concurrent users performing task operations without performance degradation.
- **SC-005**: The Chat API remains responsive (responds within 5 seconds) even when the Notification Service and Audit Service are completely unavailable.
- **SC-006**: 100% of task state changes are captured in the audit trail with no events lost, even during transient service outages (verified over a 24-hour test window).
- **SC-007**: The system deploys and runs successfully on both a local Minikube cluster and a production-grade cloud Kubernetes cluster.
- **SC-008**: Zero hardcoded infrastructure connection strings exist in any service's application code (verified by automated scan).
- **SC-009**: All three services (Chat API, Notification Service, Recurring Engine) can be independently deployed and scaled without affecting other services.
- **SC-010**: Scheduled reminders fire within 30 seconds of their target time under normal operating conditions.

## Assumptions

- The Phase 2 chatbot NLP/intent-recognition logic will be reused and adapted for the new event-driven architecture.
- PostgreSQL (via Neon or standard deployment) is the backing store for the Dapr state component.
- Apache Kafka (via Strimzi operator on Kubernetes or managed Kafka) is the backing broker for the Dapr Pub/Sub component.
- The frontend (Next.js from Phase 2) will be adapted to consume real-time updates via WebSocket or Server-Sent Events, with the backend publishing to the `task-updates` topic.
- Dapr Jobs API (alpha1) is available and functional in the target Dapr runtime version.
- Browser notifications (Push API or similar) are the primary notification channel; additional channels (email, SMS) are out of scope for this iteration.
- The three backend services are: `chat-api`, `notification-service`, and `recurring-engine`, as defined in the project constitution.
- Python 3.11+ with FastAPI is the runtime for all three services, as mandated by the constitution.

## Non-Goals

- Multi-tenant or multi-organization support (single-tenant for this iteration).
- Email or SMS notification channels (browser push only).
- Task sharing or collaboration features between users.
- Complex task dependencies (e.g., task A blocks task B).
- Natural language processing model training or fine-tuning (using existing Phase 2 NLP capabilities).
- Mobile native application (web-only).

## Dependencies

- **Phase 2 (todo-phase-2)**: Source codebase for chatbot UI, NLP logic, and task data model.
- **Dapr Runtime**: Provides Pub/Sub, State Management, Jobs API, and Secrets API building blocks.
- **Apache Kafka**: Event bus for all inter-service communication (accessed only through Dapr).
- **PostgreSQL**: Persistent state store (accessed only through Dapr State API).
- **Kubernetes**: Container orchestration for local (Minikube) and production deployment.
- **Helm**: Package manager for Kubernetes deployments.
