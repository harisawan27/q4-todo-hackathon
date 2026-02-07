# Tasks: Cloud-Native Event-Driven Task System

**Input**: Design documents from `/specs/002-cloud-native-event-driven/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included (not explicitly requested in the feature specification). Add test tasks separately if needed.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend services**: `services/{service-name}/app/`
- **Frontend**: `frontend/`
- **Shared modules**: `shared/`
- **Infrastructure**: `dapr-components/`, `k8s-manifests/`, `helm/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding, shared modules, and Dapr component configuration

- [ ] T001 Create top-level project directory structure with `services/chat-api/`, `services/notification-service/`, `services/recurring-engine/`, `shared/logging/`, `dapr-components/local/`, `dapr-components/production/`, `k8s-manifests/base/`, `helm/donekaro/`, `scripts/`
- [ ] T002 [P] Create `shared/logging/__init__.py` and `shared/logging/config.py` with `JSONFormatter` class and `setup_logging(service_name, level)` function emitting structured JSON to stdout per plan.md §6.1 (fields: timestamp, level, service, trace_id, message)
- [ ] T003 [P] Create `services/chat-api/requirements.txt` with dependencies: fastapi, uvicorn, httpx, litellm, pydantic, python-dotenv
- [ ] T004 [P] Create `services/notification-service/requirements.txt` with dependencies: fastapi, uvicorn, httpx, pydantic, pywebpush, py-vapid
- [ ] T005 [P] Create `services/recurring-engine/requirements.txt` with dependencies: fastapi, uvicorn, httpx, pydantic, croniter
- [ ] T006 [P] Create `services/chat-api/pyproject.toml` with project metadata, ruff config, and pytest config
- [ ] T007 [P] Create `services/notification-service/pyproject.toml` with project metadata, ruff config, and pytest config
- [ ] T008 [P] Create `services/recurring-engine/pyproject.toml` with project metadata, ruff config, and pytest config
- [ ] T009 [P] Create `dapr-components/local/statestore-postgres.yaml` — Dapr State Store component (`state.postgresql.v2`) with `secretKeyRef` for connection string per research.md R1
- [ ] T010 [P] Create `dapr-components/local/pubsub-kafka.yaml` — Dapr Pub/Sub component (`pubsub.kafka`) for local Strimzi broker per research.md R2
- [ ] T011 [P] Create `dapr-components/local/secretstore-local.yaml` — Dapr local file secret store (`secretstores.local.file`) pointing to `secrets.json` per research.md R6
- [ ] T012 [P] Create `dapr-components/local/subscriptions.yaml` — Declarative Dapr Subscription CRDs for all three services per `contracts/dapr-subscriptions.yaml`
- [ ] T013 [P] Create `dapr-components/production/statestore-postgres.yaml` — Production PostgreSQL state store with Kubernetes Secrets auth
- [ ] T014 [P] Create `dapr-components/production/pubsub-kafka.yaml` — Production Kafka (Redpanda Cloud) with SASL_SSL auth per research.md R2
- [ ] T015 [P] Create `dapr-components/production/secretstore-k8s.yaml` — Production Kubernetes Secrets store
- [ ] T016 [P] Create `dapr-components/production/subscriptions.yaml` — Production Dapr subscriptions (same routes, production namespace)
- [ ] T017 [P] Create `.gitignore` entries for `secrets.json`, `*.pyc`, `__pycache__/`, `.env`, `node_modules/`, `.next/`
- [ ] T018 Create `dapr.yaml` — Dapr multi-app run configuration for local development with all three services (chat-api:8000/3500, notification-service:8001/3501, recurring-engine:8002/3502)
- [ ] T019 Create `docker-compose.yaml` — Local dev compose with Redpanda (Kafka), Dapr sidecars (standalone mode), placement service, and all three backend services per plan.md §7.5

**Checkpoint**: Project structure created, shared modules ready, Dapr components configured for local dev

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure modules that ALL user stories depend on — Dapr client wrappers, base models, middleware, and service skeletons

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Shared Dapr Client Wrappers

- [ ] T020 [P] Create `services/chat-api/app/dapr_client.py` — Async Dapr HTTP client wrapper with `publish_event()`, `get_state()`, `save_state()`, `delete_state()`, `get_secret()`, `bulk_get_state()`, `transact_state()` using httpx per plan.md §6.2
- [ ] T021 [P] Create `services/notification-service/app/dapr_client.py` — Async Dapr HTTP client wrapper (same pattern as chat-api)
- [ ] T022 [P] Create `services/recurring-engine/app/dapr_client.py` — Async Dapr HTTP client wrapper with additional `register_job()`, `delete_job()`, `get_job()` methods for Dapr Jobs API alpha1 per research.md R3

### Base Models (Shared Across Stories)

- [ ] T023 [P] Create `services/chat-api/app/models/__init__.py` and `services/chat-api/app/models/task.py` — `Task`, `TaskCreate`, `TaskUpdate`, `TaskIndex`, `TaskStatus`, `TaskPriority` Pydantic models per data-model.md §1
- [ ] T024 [P] Create `services/chat-api/app/models/events.py` — `TaskEvent`, `TaskEventType`, `TaskUpdateBroadcast` Pydantic models for CloudEvents payloads per data-model.md §4 and event-schemas.yaml
- [ ] T025 [P] Create `services/chat-api/app/models/conversation.py` — `ConversationContext`, `Message`, `MessageRole` Pydantic models per data-model.md §7
- [ ] T026 [P] Create `services/recurring-engine/app/models/__init__.py` and `services/recurring-engine/app/models/recurrence.py` — `RecurrenceRule`, `RecurrenceRuleCreate`, `RecurrenceFrequency`, `RecurrenceEndCondition` Pydantic models per data-model.md §2
- [ ] T027 [P] Create `services/recurring-engine/app/models/job.py` — `JobRegistration`, `JobCallback` Pydantic models for Dapr Jobs API payloads per research.md R3
- [ ] T028 [P] Create `services/notification-service/app/models/__init__.py` and `services/notification-service/app/models/notification.py` — `Notification`, `NotificationType` Pydantic models per data-model.md §5
- [ ] T029 [P] Create `services/notification-service/app/models/subscription.py` — `PushSubscription`, `PushSubscriptionIndex` Pydantic models per data-model.md §6

### Core Service Layers

- [ ] T030 Create `services/chat-api/app/services/__init__.py` and `services/chat-api/app/services/state_service.py` — Dapr State Management wrapper with `save_task()`, `get_task()`, `list_user_tasks()`, `delete_task()`, `update_task_index()` using index-key pattern and ETag concurrency per research.md R1
- [ ] T031 [P] Create `services/chat-api/app/services/pubsub_service.py` — Dapr Pub/Sub wrapper with `publish_task_event()`, `publish_task_update_broadcast()` using CloudEvents envelope per research.md R2, including partition key metadata
- [ ] T032 [P] Create `services/chat-api/app/services/secret_service.py` — Dapr Secrets wrapper with `get_secret()` for Gemini API key and JWT secret

### Middleware & Config

- [ ] T033 Create `services/chat-api/app/config.py` — Pydantic Settings class reading `SERVICE_NAME`, `LOG_LEVEL`, `DAPR_HTTP_PORT` from env vars, plus `load_secrets()` async method using Dapr Secrets API per plan.md §8.1
- [ ] T034 [P] Create `services/chat-api/app/middleware/__init__.py` and `services/chat-api/app/middleware/auth.py` — JWT Bearer validation middleware extracting user_id from token per plan.md §8.1 (adapted from Phase 2 `auth/jwt_bearer.py`)
- [ ] T035 [P] Create `services/chat-api/app/middleware/logging.py` — Request/response logging middleware using shared JSON logger with trace_id propagation

### Service Skeletons (FastAPI Apps)

- [ ] T036 Create `services/chat-api/app/__init__.py` and `services/chat-api/app/main.py` — FastAPI app entry point with lifespan, middleware registration, router includes, health endpoint, and Dapr subscription endpoint per plan.md §1.1
- [ ] T037 [P] Create `services/notification-service/app/__init__.py`, `services/notification-service/app/config.py`, and `services/notification-service/app/main.py` — FastAPI app with lifespan, health endpoint, and Dapr event handler routes per plan.md §1.2
- [ ] T038 [P] Create `services/recurring-engine/app/__init__.py`, `services/recurring-engine/app/config.py`, and `services/recurring-engine/app/main.py` — FastAPI app with lifespan, health endpoint, Dapr event handler routes, and Jobs callback route per plan.md §1.3

### Health Endpoints

- [ ] T039 Create `services/chat-api/app/routes/__init__.py` and `services/chat-api/app/routes/health.py` — `GET /health` returning `HealthResponse` with Dapr sidecar connectivity check (state store + pubsub availability) per chat-api-openapi.yaml

### Dockerfiles

- [ ] T040 [P] Create `services/chat-api/Dockerfile` — Multi-stage Python 3.11-slim build with non-root user, port 8000, shared logging copy per plan.md §7.1
- [ ] T041 [P] Create `services/notification-service/Dockerfile` — Multi-stage Python 3.11-slim build with non-root user, port 8001 per plan.md §7.1
- [ ] T042 [P] Create `services/recurring-engine/Dockerfile` — Multi-stage Python 3.11-slim build with non-root user, port 8002 per plan.md §7.1

**Checkpoint**: Foundation ready — all Dapr wrappers, models, middleware, and service skeletons in place. User story implementation can now begin.

---

## Phase 3: User Story 1 — Conversational Task Management via Chatbot (Priority: P1) 🎯 MVP

**Goal**: Users interact via natural language to create, update, query, complete, and delete tasks. All task operations produce events to Kafka via Dapr. The chatbot uses LiteLLM/Gemini for intent recognition and tool calling.

**Independent Test**: Send natural language messages to `POST /chat` and verify tasks are created/updated/deleted in the Dapr state store and `task-created`/`task-updated`/`task-completed`/`task-deleted` events are published to the `task-events` topic.

### Implementation for User Story 1

- [ ] T043 [US1] Create `services/chat-api/app/services/task_service.py` — Task business logic orchestrator with `create_task()`, `get_task()`, `list_tasks()`, `update_task()`, `delete_task()`, `complete_task()`, `find_task_by_title()`. Each method: saves state via `state_service`, publishes event via `pubsub_service`, publishes broadcast via `pubsub_service`. Uses ETag concurrency for updates/completes/deletes per FR-017.
- [ ] T044 [US1] Create `services/chat-api/app/chatbot/__init__.py` and `services/chat-api/app/chatbot/tools.py` — LiteLLM tool functions: `add_task(title, description, priority, due_date, tags)`, `list_tasks()`, `complete_task(title)`, `update_task(title, new_title, new_description, new_priority)`, `delete_task(title)`, `find_task_by_title(title)`. Each function calls `task_service` methods. Tool functions must have JSON Schema compatible signatures for LiteLLM tool_choice per plan.md §8.1.
- [ ] T045 [US1] Create `services/chat-api/app/chatbot/runner.py` — LiteLLM agent runner adapted from Phase 2. Initializes LiteLLM with Gemini model, registers tool functions from `tools.py`, manages conversation context via `state_service` (save/load `ConversationContext`), sends user message, processes tool calls, returns final assistant response. Loads Gemini API key via `secret_service` per FR-015.
- [ ] T046 [US1] Create `services/chat-api/app/routes/chat.py` — `POST /chat` endpoint accepting `ChatRequest`, extracting user_id from JWT middleware, calling `runner.process_message()`, returning `ChatResponse` with optional `task_action` per chat-api-openapi.yaml. Handle conversation_id for session continuity.
- [ ] T047 [US1] Create `services/chat-api/app/routes/tasks.py` — REST endpoints `GET /tasks`, `GET /tasks/{taskId}`, `PUT /tasks/{taskId}`, `DELETE /tasks/{taskId}`, `POST /tasks/{taskId}/complete` per chat-api-openapi.yaml. All endpoints use JWT auth middleware, call `task_service`, return proper HTTP status codes (200, 204, 404, 409). `PUT` and `POST /complete` accept `If-Match` ETag header per FR-017.
- [ ] T048 [US1] Create `services/chat-api/app/routes/subscriptions.py` — `GET /dapr/subscribe` returning programmatic Dapr subscription list for `task-updates` topic (fallback if declarative CRDs not used) per chat-api-openapi.yaml
- [ ] T049 [US1] Register all routes in `services/chat-api/app/main.py` — Include `chat`, `tasks`, `health`, `subscriptions`, `events` routers with appropriate prefixes

**Checkpoint**: User Story 1 complete — users can converse with the chatbot to CRUD tasks, events are published to Kafka, REST API available for direct task operations

---

## Phase 4: User Story 2 — Recurring Tasks and Due Dates (Priority: P2)

**Goal**: Users set recurring schedules and due dates via the chatbot. The recurring-engine manages Dapr Jobs for scheduling, generates next instances on completion, and publishes reminder events.

**Independent Test**: Create a recurring task via chatbot, complete it, and verify the next instance is auto-generated in the state store with the correct future date. Create a task with a due date and verify a reminder job is registered via Dapr Jobs API.

### Implementation for User Story 2

- [ ] T050 [P] [US2] Create `services/recurring-engine/app/services/__init__.py` and `services/recurring-engine/app/services/state_service.py` — Dapr State wrapper for recurring-engine with `save_recurrence_rule()`, `get_recurrence_rule()`, `save_reminder()`, `get_reminder()`, `save_idempotency_marker()`, `check_idempotency()` per data-model.md §2, §3
- [ ] T051 [P] [US2] Create `services/recurring-engine/app/services/pubsub_service.py` — Dapr Pub/Sub wrapper for recurring-engine with `publish_task_event()` (for recurrence-generated events to `task-events`) and `publish_reminder_event()` (to `reminders` topic) per plan.md §1.3
- [ ] T052 [US2] Create `services/recurring-engine/app/services/recurrence_service.py` — Recurrence rule evaluation with `calculate_next_occurrence(rule)` supporting DAILY, WEEKLY, WEEKDAY, MONTHLY, CUSTOM frequencies per data-model.md §2. Validate rules per FR-018 (reject Feb 30, day_of_month > 28 for monthly). Use `croniter` for CUSTOM cron expressions. Handle edge case: skip past dates, generate only future instances per spec.md edge cases.
- [ ] T053 [US2] Create `services/recurring-engine/app/services/job_service.py` — Dapr Jobs API wrapper with `register_recurring_job(task_id, cron_schedule)`, `register_reminder_job(task_id, trigger_time)`, `cancel_job(job_name)`, `get_job_status(job_name)` per research.md R3. Job naming: `recurrence-{taskId}`, `reminder-{taskId}`. Uses alpha1 API path.
- [ ] T054 [US2] Create `services/recurring-engine/app/handlers/__init__.py` and `services/recurring-engine/app/handlers/task_event_handler.py` — Dapr event handlers: `POST /events/task-created` (if has due_date → register reminder job), `POST /events/task-completed` (if has recurrence_rule_id → fetch rule, calculate next occurrence, create new task instance via transactional state save, publish `task-recurrence-generated` event, register next job), `POST /events/task-updated` (if due_date changed → cancel old reminder, register new one), `POST /events/task-deleted` (cancel any associated jobs). Include idempotency checks per research.md R3.
- [ ] T055 [US2] Create `services/recurring-engine/app/handlers/job_callback_handler.py` — `PUT /job/{job_name}` Dapr Jobs callback handler. Parse job type from payload data. For `recurrence-trigger`: evaluate recurrence rule, generate next task instance, publish events. For `reminder-fired`: publish reminder event to `reminders` topic. Include idempotency guard per research.md R3.
- [ ] T056 [US2] Update `services/chat-api/app/chatbot/tools.py` — Extend `add_task()` to accept `recurrence_rule` parameter (RecurrenceRuleCreate). When present, publish `task-created` event with recurrence data so recurring-engine can pick it up. Extend `complete_task()` response to indicate if next instance will be auto-generated (`hasRecurrence: true` in event payload).
- [ ] T057 [US2] Update `services/chat-api/app/models/task.py` — Ensure `TaskCreate` includes optional `recurrence_rule: RecurrenceRuleCreate` field per data-model.md §1
- [ ] T058 [US2] Register event handler routes and job callback route in `services/recurring-engine/app/main.py`

**Checkpoint**: User Story 2 complete — recurring tasks auto-generate next instances, due-date reminders are scheduled, recurring-engine processes task lifecycle events

---

## Phase 5: User Story 3 — Real-Time Notifications and Cross-Client Updates (Priority: P2)

**Goal**: Push notifications delivered when reminders fire. All connected clients see task changes in real-time via SSE without page refresh. Notification service is decoupled — Chat API remains functional even if notifications are down.

**Independent Test**: Trigger a reminder event on the `reminders` topic and verify the notification-service delivers a browser push notification. Modify a task on one client and verify the SSE stream delivers the update to another connected client.

### Implementation for User Story 3

- [ ] T059 [P] [US3] Create `services/notification-service/app/services/__init__.py` and `services/notification-service/app/services/state_service.py` — Dapr State wrapper for notification-service with `save_notification()`, `get_push_subscriptions()`, `save_push_subscription()`, `delete_push_subscription()`, `update_push_subscription_index()` per data-model.md §5, §6
- [ ] T060 [P] [US3] Create `services/notification-service/app/services/push_service.py` — Browser Web Push delivery using `pywebpush` library. Methods: `send_notification(subscription, title, body, url)`, `send_to_user(user_id, title, body, url)` (fetches all push subscriptions for user, sends to each). Handle 410 Gone (remove subscription), 5xx (return RETRY for Dapr redelivery). Load VAPID keys via Dapr Secrets API per FR-015.
- [ ] T061 [US3] Create `services/notification-service/app/handlers/__init__.py` and `services/notification-service/app/handlers/reminder_handler.py` — `POST /events/reminder-fired` and `POST /events/recurring-trigger` handlers. Extract task title, due date, user_id from event payload. Call `push_service.send_to_user()`. Save notification record via `state_service`. Update reminder status to delivered. Return `SUCCESS`/`RETRY`/`DROP` per Dapr protocol. Per plan.md §4.3 sequence 3.
- [ ] T062 [US3] Create `services/notification-service/app/handlers/task_update_handler.py` — `POST /events/task-updates` handler for cross-client propagation. Extract task update broadcast data. Call `push_service.send_to_user()` with task change summary. Per plan.md §1.2.
- [ ] T063 [US3] Create `services/chat-api/app/routes/events.py` — `GET /events/stream` SSE endpoint. Maintain in-memory dict of `user_id → list[asyncio.Queue]`. `POST /events/task-updates` Dapr subscription handler that pushes events to queues. SSE generator yields events with `id`, `event: task-update`, `data: JSON`. Include 30s keepalive heartbeat. Handle client disconnect cleanup. Per research.md R5 and plan.md §5.2.
- [ ] T064 [US3] Create `services/chat-api/app/routes/push.py` — `POST /push/subscribe` and `POST /push/unsubscribe` endpoints per chat-api-openapi.yaml. Proxy subscription data to notification-service state store via Dapr Service Invocation or direct state save.
- [ ] T065 [US3] Register event handler routes in `services/notification-service/app/main.py` — Include `reminder_handler` and `task_update_handler` routes
- [ ] T066 [US3] Register SSE and push routes in `services/chat-api/app/main.py` — Include `events` and `push` routers

**Checkpoint**: User Story 3 complete — push notifications delivered on reminders, SSE provides real-time cross-client updates, system degrades gracefully if notification-service is down (FR-009)

---

## Phase 6: User Story 4 — Audit Trail for Task History (Priority: P3)

**Goal**: Every task state change is logged by an audit consumer. Users can query task history to see a chronological timeline of all changes with timestamps, action types, and before/after states.

**Independent Test**: Perform task CRUD operations and query the audit log via chatbot (`"Show history for 'Buy groceries'"`) to verify all changes are recorded with correct timestamps, action types, and before/after states.

### Implementation for User Story 4

- [ ] T067 [P] [US4] Create `services/chat-api/app/models/audit.py` — `AuditRecord`, `AuditAction` Pydantic models per data-model.md §8
- [ ] T068 [US4] Create `services/chat-api/app/services/audit_service.py` — Audit consumer that subscribes to `task-events` topic, processes each event type (created, updated, completed, deleted, recurrence-generated), creates `AuditRecord` with before/after state, saves to Dapr state store with key `audit||{audit-id}` and index `audit-index||{task-id}`. Methods: `log_audit_event(task_event)`, `get_task_history(task_id)` (returns chronological list of audit records).
- [ ] T069 [US4] Create `services/chat-api/app/routes/audit.py` — Dapr subscription handler `POST /events/audit-task-events` for consuming `task-events` topic. Also add `GET /tasks/{taskId}/history` REST endpoint returning audit trail for a task per spec.md US4 scenario 2.
- [ ] T070 [US4] Update `services/chat-api/app/chatbot/tools.py` — Add `show_task_history(title)` tool function that calls `audit_service.get_task_history()` and formats results as a chronological timeline for chatbot response per spec.md US4 scenario 2.
- [ ] T071 [US4] Update Dapr subscription configuration in `dapr-components/local/subscriptions.yaml` — Add chat-api as additional consumer of `task-events` topic scoped for audit handling (route to `/events/audit-task-events`)
- [ ] T072 [US4] Register audit routes in `services/chat-api/app/main.py` — Include audit event handler and history endpoint

**Checkpoint**: User Story 4 complete — all task changes are logged, users can query task history via chatbot or REST API

---

## Phase 7: Frontend Integration

**Purpose**: Refactor the Phase 2 Next.js frontend for the event-driven architecture — update API calls, add SSE client, remove deprecated code

- [ ] T073 [P] Create `frontend/lib/sse-client.ts` — `useTaskUpdates(userId)` React hook using `EventSource` connected to `/api/events/stream`. On `task-update` event, invalidate TanStack Query `["tasks"]` cache. Handle auto-reconnect and error logging. Per plan.md §8.2 and research.md R5.
- [ ] T074 Update `frontend/lib/api.ts` — Change `API_URL` to same-origin (`""`), remove `{userId}` from chat endpoint path (`/api/chat` instead of `/api/{userId}/chat`), update all endpoint paths to match chat-api-openapi.yaml contracts.
- [ ] T075 [P] Update `frontend/components/` (chat widget) — Integrate `useTaskUpdates` hook in dashboard layout for real-time task list updates across clients. Per plan.md §8.2.
- [ ] T076 [P] Create `frontend/Dockerfile` — Multi-stage Node.js 20-alpine build with standalone output per plan.md §7.1 frontend Dockerfile specification. Configure `next.config.ts` with `output: "standalone"`.

**Checkpoint**: Frontend integrated — real-time updates via SSE, API calls routed through Ingress, push subscription support

---

## Phase 8: Kubernetes & Helm Deployment

**Purpose**: Kubernetes manifests, Helm charts, and deployment scripts for local (Minikube) and production (AKS/GKE)

### Kubernetes Manifests

- [ ] T077 [P] Create `k8s-manifests/base/namespace.yaml` — Kubernetes namespace `donekaro`
- [ ] T078 [P] Create `k8s-manifests/base/chat-api/deployment.yaml` and `k8s-manifests/base/chat-api/service.yaml` — Deployment with Dapr annotations (`dapr.io/enabled`, `dapr.io/app-id: chat-api`, `dapr.io/app-port: 8000`), liveness/readiness probes at `/health`, resource requests/limits per plan.md §7.2
- [ ] T079 [P] Create `k8s-manifests/base/chat-api/hpa.yaml` — HorizontalPodAutoscaler targeting 70% CPU, min 1 max 5 replicas
- [ ] T080 [P] Create `k8s-manifests/base/notification-service/deployment.yaml` and `k8s-manifests/base/notification-service/service.yaml` — Deployment with Dapr annotations (app-id: notification-service, port: 8001) per plan.md §7.2
- [ ] T081 [P] Create `k8s-manifests/base/recurring-engine/deployment.yaml` and `k8s-manifests/base/recurring-engine/service.yaml` — Deployment with Dapr annotations (app-id: recurring-engine, port: 8002) per plan.md §7.2
- [ ] T082 [P] Create `k8s-manifests/base/frontend/deployment.yaml` and `k8s-manifests/base/frontend/service.yaml` — Deployment for Next.js frontend on port 3000
- [ ] T083 [P] Create `k8s-manifests/base/infrastructure/kafka/kafka-cluster.yaml` — Strimzi Kafka CRD (single broker, ephemeral storage for local) per research.md R4
- [ ] T084 [P] Create `k8s-manifests/base/infrastructure/kafka/kafka-topics.yaml` — KafkaTopic CRDs for `task-events` (7d retention), `reminders` (3d), `task-updates` (1d) per research.md R4
- [ ] T085 [P] Create `k8s-manifests/base/infrastructure/secrets/secrets-template.yaml` — Template for Kubernetes Secrets (postgres-credentials, gemini-credentials, vapid-credentials, auth-credentials)
- [ ] T086 Create `k8s-manifests/base/kustomization.yaml` — Kustomize base referencing all resources
- [ ] T087 [P] Create `k8s-manifests/overlays/local/kustomization.yaml` — Minikube overlay with replica=1 patches, ephemeral storage
- [ ] T088 [P] Create `k8s-manifests/overlays/production/kustomization.yaml` — Production overlay with increased replicas, resource limits, HPA enabled

### Helm Charts

- [ ] T089 Create `helm/donekaro/Chart.yaml` — Chart metadata with appVersion matching release
- [ ] T090 Create `helm/donekaro/values.yaml` — Default Helm values for all services per plan.md §7.2 (chatApi, notificationService, recurringEngine, frontend, kafka, dapr config)
- [ ] T091 [P] Create `helm/donekaro/values-local.yaml` — Minikube overrides (replicas=1, imagePullPolicy=IfNotPresent, kafka.enabled=true)
- [ ] T092 [P] Create `helm/donekaro/values-production.yaml` — Production overrides per plan.md §7.2 (replicas, HPA, ACR registry, kafka.enabled=false for Redpanda Cloud)
- [ ] T093 Create `helm/donekaro/templates/_helpers.tpl` — Template helpers for labels, names, selectors, Dapr annotations
- [ ] T094 [P] Create `helm/donekaro/templates/chat-api-deployment.yaml` — Helm-templated chat-api Deployment + Service per plan.md §7.2 deployment template
- [ ] T095 [P] Create `helm/donekaro/templates/notification-service-deployment.yaml` — Helm-templated notification-service Deployment + Service
- [ ] T096 [P] Create `helm/donekaro/templates/recurring-engine-deployment.yaml` — Helm-templated recurring-engine Deployment + Service
- [ ] T097 [P] Create `helm/donekaro/templates/frontend-deployment.yaml` — Helm-templated frontend Deployment + Service + Ingress with path-based routing (`/api/*` → chat-api, `/` → frontend) per plan.md §8.2

### Deployment Scripts

- [ ] T098 [P] Create `scripts/local-setup.sh` — Minikube + Dapr + Strimzi setup script per quickstart.md Option A steps 1-4
- [ ] T099 [P] Create `scripts/deploy-local.sh` — Build Docker images, load into Minikube, deploy with Helm per quickstart.md steps 7-8
- [ ] T100 [P] Create `scripts/deploy-production.sh` — Production deployment script using Helm with production values

**Checkpoint**: Kubernetes deployment ready — services deployable on Minikube (local) and production K8s cluster

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: CI/CD pipeline, edge case handling, and final hardening

- [ ] T101 [P] Create `.github/workflows/deploy.yaml` — GitHub Actions CI/CD pipeline with lint-test (3 services parallel), frontend-build, build-images, integration-test, deploy-production jobs per plan.md §7.3
- [ ] T102 Add edge case handling in `services/chat-api/app/chatbot/runner.py` — Handle unrecognizable messages with helpful clarification prompt per spec.md edge cases (not fail silently)
- [ ] T103 Add edge case handling in `services/chat-api/app/services/state_service.py` — Graceful retry on state store unreachable per spec.md edge cases; return user-friendly error
- [ ] T104 Add edge case handling in `services/chat-api/app/services/pubsub_service.py` — Graceful handling when event bus is unavailable per spec.md edge cases; store tasks locally, queue events for later publish (FR-009)
- [ ] T105 [P] Add edge case handling in `services/recurring-engine/app/services/recurrence_service.py` — Handle past-date recurrence instances (generate only next future instance, no backfill) per spec.md edge cases
- [ ] T106 [P] Create zero-hardcoded-secrets validation — Script or lint rule to scan all service `app/` directories for hardcoded connection strings, API keys, or credentials per SC-008
- [ ] T107 Run `quickstart.md` validation — Execute Option B (Docker Compose) or Option C (Dapr multi-app run) end-to-end and verify health check, chat message, and SSE stream per quickstart.md verification steps

**Checkpoint**: System hardened, CI/CD ready, all edge cases handled, zero hardcoded secrets verified

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phase 3 (US1 - Chatbot)**: Depends on Phase 2 — MVP, must complete first
- **Phase 4 (US2 - Recurring)**: Depends on Phase 2; integrates with US1 task events
- **Phase 5 (US3 - Notifications)**: Depends on Phase 2; consumes events from US1/US2
- **Phase 6 (US4 - Audit)**: Depends on Phase 2; consumes events from US1
- **Phase 7 (Frontend)**: Can start after Phase 2; benefits from Phase 3 (US1) being done
- **Phase 8 (K8s/Helm)**: Can start after Phase 1 (infrastructure only, no app code dependency)
- **Phase 9 (Polish)**: Depends on Phases 3-7 being substantially complete

### User Story Dependencies

- **US1 (P1 — Chatbot CRUD)**: No story dependencies — can start immediately after Phase 2
- **US2 (P2 — Recurring Tasks)**: Consumes `task-events` from US1 → can start in parallel but needs US1 events to test
- **US3 (P2 — Notifications)**: Consumes `reminders` from US2 and `task-updates` from US1 → can start in parallel but needs US1/US2 events
- **US4 (P3 — Audit Trail)**: Consumes `task-events` from US1 → can start after US1 is publishing events

### Within Each User Story

- Models before services
- Services before handlers/routes
- Core implementation before edge case handling
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T002-T017 are all parallelizable (different files, no dependencies)
- **Phase 2**: T020-T029 (Dapr clients + models) are all parallelizable; T030-T032 (services) partially parallel; T033-T035 (middleware/config) parallel; T036-T042 (skeletons + Dockerfiles) partially parallel
- **Phase 3 (US1)**: T044-T045 (tools + runner) are sequential; T047 (REST API) parallel with T046 (chat route)
- **Phase 4 (US2)**: T050-T051 parallel; T052-T053 parallel after T050-T051
- **Phase 5 (US3)**: T059-T060 parallel; T063 parallel with T061-T062
- **Phase 7 (Frontend)**: T073, T074, T075, T076 mostly parallel
- **Phase 8 (K8s/Helm)**: T077-T085 all parallelizable; T089-T097 partially parallel
- **Phase 8 can run in parallel with Phases 3-7** (infrastructure doesn't depend on app code)

---

## Parallel Example: Phase 2 (Foundational)

```bash
# Launch all Dapr client wrappers in parallel:
Task T020: "Create chat-api dapr_client.py"
Task T021: "Create notification-service dapr_client.py"
Task T022: "Create recurring-engine dapr_client.py"

# Launch all models in parallel:
Task T023: "Create Task models"
Task T024: "Create Event models"
Task T025: "Create Conversation models"
Task T026: "Create RecurrenceRule models"
Task T027: "Create Job models"
Task T028: "Create Notification models"
Task T029: "Create PushSubscription models"
```

## Parallel Example: Phase 8 (K8s Manifests)

```bash
# Launch all K8s manifests in parallel:
Task T077: "Create namespace.yaml"
Task T078: "Create chat-api deployment"
Task T080: "Create notification-service deployment"
Task T081: "Create recurring-engine deployment"
Task T082: "Create frontend deployment"
Task T083: "Create Kafka cluster CRD"
Task T084: "Create Kafka topics CRD"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (Chatbot CRUD)
4. **STOP and VALIDATE**: Test chatbot task creation, listing, updating, completing, deleting
5. Deploy to Docker Compose for demo

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. User Story 1 (Chatbot) → Test independently → Docker Compose demo (MVP!)
3. User Story 2 (Recurring) → Test recurring task generation → Demo
4. User Story 3 (Notifications) → Test push notifications + SSE → Demo
5. User Story 4 (Audit) → Test task history → Demo
6. Frontend + K8s → Full stack deployment → Production-ready demo
7. Polish → CI/CD, edge cases → Release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Chatbot CRUD) — **PRIORITY**
   - Developer B: Phase 8 (K8s/Helm) — infrastructure can proceed in parallel
3. After US1 is publishing events:
   - Developer A: User Story 2 (Recurring)
   - Developer C: User Story 3 (Notifications)
   - Developer D: User Story 4 (Audit)
   - Developer B: Frontend integration
4. All stories integrate via Kafka events — minimal cross-story code conflicts

---

## Notes

- [P] tasks = different files, no dependencies between them
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- All inter-service communication is via Kafka/Dapr — no direct HTTP between services
- Zero direct infrastructure imports in application code (Constitution III — NON-NEGOTIABLE)
- All state access through Dapr State API with index-key pattern (PostgreSQL v2)
- All secrets via Dapr Secrets API (no hardcoded credentials)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
