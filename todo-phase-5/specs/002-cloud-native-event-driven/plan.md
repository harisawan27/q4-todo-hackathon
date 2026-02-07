# Implementation Plan: Cloud-Native Event-Driven Task System

**Branch**: `002-cloud-native-event-driven` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-cloud-native-event-driven/spec.md`

## Summary

Refactor the Phase 2 monolithic FastAPI/Next.js todo application into a Dapr-enabled, event-driven microservices architecture comprising three independently deployable services: **chat-api** (user-facing FastAPI), **notification-service** (Python worker consuming reminders), and **recurring-engine** (Python worker managing scheduled jobs). All inter-service communication flows through Apache Kafka via the Dapr Pub/Sub building block. State persistence uses PostgreSQL exclusively through the Dapr State Management API. Scheduling uses the Dapr Jobs API (alpha1). Secrets are resolved via the Dapr Secrets API backed by Kubernetes Secrets. The frontend (Next.js) is refactored to consume real-time updates via Server-Sent Events bridged from the `task-updates` Kafka topic.

## Technical Context

**Language/Version**: Python 3.11+ (all three backend services), TypeScript/Node.js 20+ (Next.js frontend)
**Primary Dependencies**:
- Backend: FastAPI, uvicorn, httpx (Dapr HTTP client), litellm (AI/Gemini), pydantic
- Frontend: Next.js 16, React 19, TanStack Query, Better-Auth
- Infrastructure: Dapr 1.14+, Apache Kafka (Strimzi operator), PostgreSQL (Neon DB), Kubernetes
**Storage**: PostgreSQL via Dapr State Management API (statestore-postgres component); Kafka for event streaming
**Testing**: pytest (unit + integration), Dapr test containers for integration tests
**Target Platform**: Kubernetes (Minikube for local, AKS/GKE for production)
**Project Type**: Microservices (3 backend services + 1 frontend)
**Performance Goals**: <3s task creation e2e, <2s notification delivery, <5s recurring task generation, 100+ concurrent users (SC-001 through SC-010)
**Constraints**: Zero direct infrastructure imports in app code (Constitution III - NON-NEGOTIABLE), all inter-service via Kafka/Dapr, ETag optimistic locking, structured JSON logging
**Scale/Scope**: 3 microservices, 3 Kafka topics, 1 state store, 1 secret store, Helm charts for deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Cloud-Native Microservices | PASS | Three services defined: chat-api, notification-service, recurring-engine. Each gets own Dockerfile, requirements.txt, independent deployment. |
| II | Event-Driven Architecture (EDA) | PASS | All inter-service communication via Kafka topics (task-events, reminders, task-updates). No synchronous HTTP between services. |
| III | Dapr Sidecar Abstraction (NON-NEGOTIABLE) | PASS | All Kafka access via Dapr Pub/Sub API. All state via Dapr State API. All secrets via Dapr Secrets API. Zero direct infrastructure imports. |
| IV | Dapr Jobs Scheduling | PASS | Recurring task triggers and reminder scheduling via Dapr Jobs API (alpha1). No cron polling or sleep timers. |
| V | Dapr State Management | PASS | Conversation history and task state via Dapr State API with PostgreSQL backend. Key pattern: `{service}||{entity}||{id}`. ETags for concurrency. |
| VI | Dapr Secrets for Security | PASS | Gemini API key, DB connection string, and all credentials via Dapr Secrets API. Kubernetes Secrets as backing store. `.env` only for local dev. |
| VII | Structured JSON Logging | PASS | Shared logging module emitting JSON to stdout with required fields (timestamp, level, service, trace_id, message). No print() statements. |

**Gate Result**: ALL PASS - Proceeding to Phase 0.

---

## 1. Service Decomposition & Boundaries

### 1.1 chat-api (FastAPI — User-Facing)

**Responsibility**: Accepts user natural-language messages, orchestrates AI intent recognition (LiteLLM/Gemini), performs task CRUD via Dapr State API, publishes domain events to Kafka via Dapr Pub/Sub, serves SSE endpoint for real-time client updates.

**Owns**:
- Chatbot conversation management (NLP, intent resolution, tool calling)
- Task CRUD operations (create, read, update, delete, complete)
- Event publishing to `task-events` topic
- Real-time SSE bridge consuming from `task-updates` topic
- Authentication validation (JWT from Better-Auth)

**Does NOT own**:
- Notification delivery (delegated to notification-service)
- Recurring task scheduling/generation (delegated to recurring-engine)
- Audit logging (consumed by downstream services)

**Dapr Building Blocks Used**:
- Pub/Sub (publish to `task-events`, subscribe to `task-updates` for SSE bridge)
- State Management (conversation context, task state)
- Secrets (Gemini API key, DB credentials)

### 1.2 notification-service (Python Worker)

**Responsibility**: Consumes reminder events from the `reminders` topic, delivers browser push notifications, and tracks delivery status.

**Owns**:
- Notification delivery (browser Push API)
- Push subscription management (state store)
- Notification history and read status
- Delivery retry logic

**Subscribes to**:
- `reminders` topic (reminder-fired events from recurring-engine)
- `task-updates` topic (for cross-client real-time propagation)

**Dapr Building Blocks Used**:
- Pub/Sub (subscribe to `reminders` and `task-updates`)
- State Management (push subscriptions, notification records)
- Secrets (VAPID keys for Web Push)

### 1.3 recurring-engine (Python Worker)

**Responsibility**: Manages recurring task schedules and due-date reminders. Registers jobs with Dapr Jobs API, handles job callbacks, generates next recurring task instances, and publishes reminder events.

**Owns**:
- Recurring task schedule management
- Dapr Jobs API registration and callback handling
- Next-instance generation when recurring task completes
- Reminder scheduling relative to due dates
- Publishing to `reminders` topic

**Subscribes to**:
- `task-events` topic (reacts to task-completed for recurrence, task-created/updated for due-date reminders)

**Publishes to**:
- `reminders` topic (reminder-fired events)
- `task-events` topic (task-recurrence-generated events)

**Dapr Building Blocks Used**:
- Pub/Sub (subscribe to `task-events`, publish to `reminders` and `task-events`)
- Jobs API (register/cancel scheduled jobs)
- State Management (recurrence rules, job metadata)
- Secrets (DB credentials if needed)

---

## 2. Directory Structure

```text
todo-phase-5/
├── services/
│   ├── chat-api/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                 # FastAPI app entry point
│   │   │   ├── config.py               # Pydantic settings (reads from Dapr Secrets)
│   │   │   ├── dapr_client.py          # Dapr HTTP client wrapper
│   │   │   ├── routes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat.py             # POST /chat - conversational endpoint
│   │   │   │   ├── tasks.py            # Task CRUD (internal, used by chatbot tools)
│   │   │   │   ├── events.py           # GET /events/stream - SSE endpoint
│   │   │   │   ├── health.py           # GET /health - liveness/readiness
│   │   │   │   └── subscriptions.py    # GET /dapr/subscribe - Dapr subscription config
│   │   │   ├── chatbot/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── runner.py           # LiteLLM agent runner (from Phase 2)
│   │   │   │   └── tools.py            # Task CRUD tool functions (adapted)
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task_service.py     # Task operations via Dapr State + event publish
│   │   │   │   ├── state_service.py    # Dapr State Management wrapper
│   │   │   │   ├── pubsub_service.py   # Dapr Pub/Sub wrapper
│   │   │   │   └── secret_service.py   # Dapr Secrets wrapper
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── task.py             # Task, TaskCreate, TaskUpdate schemas
│   │   │   │   ├── conversation.py     # Conversation, Message schemas
│   │   │   │   └── events.py           # Event payload schemas
│   │   │   └── middleware/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py             # JWT validation middleware
│   │   │       └── logging.py          # Request/response logging
│   │   ├── tests/
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── conftest.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pyproject.toml
│   │
│   ├── notification-service/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                 # FastAPI app (Dapr subscriber endpoints)
│   │   │   ├── config.py
│   │   │   ├── dapr_client.py
│   │   │   ├── handlers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── reminder_handler.py # Handles reminder-fired events
│   │   │   │   └── task_update_handler.py  # Handles task-updates for cross-client
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── push_service.py     # Browser Push API delivery
│   │   │   │   ├── state_service.py    # Dapr State wrapper
│   │   │   │   └── pubsub_service.py   # Dapr Pub/Sub wrapper
│   │   │   └── models/
│   │   │       ├── __init__.py
│   │   │       ├── notification.py     # Notification schemas
│   │   │       └── subscription.py     # Push subscription schemas
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── pyproject.toml
│   │
│   └── recurring-engine/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py                 # FastAPI app (Dapr subscriber + Jobs callback)
│       │   ├── config.py
│       │   ├── dapr_client.py
│       │   ├── handlers/
│       │   │   ├── __init__.py
│       │   │   ├── task_event_handler.py   # Reacts to task-completed for recurrence
│       │   │   └── job_callback_handler.py # Handles Dapr Jobs callbacks
│       │   ├── services/
│       │   │   ├── __init__.py
│       │   │   ├── recurrence_service.py   # Recurrence rule evaluation, next-instance
│       │   │   ├── job_service.py          # Dapr Jobs API registration/cancellation
│       │   │   ├── state_service.py        # Dapr State wrapper
│       │   │   └── pubsub_service.py       # Dapr Pub/Sub wrapper
│       │   └── models/
│       │       ├── __init__.py
│       │       ├── recurrence.py       # RecurrenceRule, Schedule schemas
│       │       └── job.py              # Job registration schemas
│       ├── tests/
│       ├── Dockerfile
│       ├── requirements.txt
│       └── pyproject.toml
│
├── shared/
│   └── logging/
│       ├── __init__.py
│       └── config.py                   # Shared structured JSON logging module
│
├── frontend/
│   ├── app/                            # Next.js App Router (from Phase 2, refactored)
│   │   ├── (auth)/
│   │   ├── dashboard/
│   │   ├── api/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   ├── lib/
│   │   ├── api.ts                      # Refactored: calls via Dapr Service Invocation
│   │   ├── sse-client.ts               # NEW: SSE client for real-time updates
│   │   └── ...
│   ├── types/
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   └── next.config.ts
│
├── dapr-components/
│   ├── local/
│   │   ├── statestore-postgres.yaml    # Dapr State Store (PostgreSQL / Neon DB)
│   │   ├── pubsub-kafka.yaml           # Dapr Pub/Sub (Kafka via Strimzi)
│   │   ├── secretstore-local.yaml      # Dapr Secret Store (local file for dev)
│   │   └── subscriptions.yaml          # Declarative topic subscriptions
│   └── production/
│       ├── statestore-postgres.yaml    # Production PostgreSQL config
│       ├── pubsub-kafka.yaml           # Production Kafka config (Redpanda Cloud)
│       ├── secretstore-k8s.yaml        # Kubernetes Secrets store
│       └── subscriptions.yaml
│
├── k8s-manifests/
│   ├── base/
│   │   ├── namespace.yaml
│   │   ├── chat-api/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── hpa.yaml                # Horizontal Pod Autoscaler
│   │   ├── notification-service/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   ├── recurring-engine/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   ├── frontend/
│   │   │   ├── deployment.yaml
│   │   │   └── service.yaml
│   │   └── infrastructure/
│   │       ├── kafka/                  # Strimzi Kafka cluster CRDs
│   │       │   ├── kafka-cluster.yaml
│   │       │   └── kafka-topics.yaml
│   │       └── secrets/
│   │           └── secrets-template.yaml
│   ├── overlays/
│   │   ├── local/                      # Minikube-specific patches
│   │   │   └── kustomization.yaml
│   │   └── production/                 # Cloud-specific patches
│   │       └── kustomization.yaml
│   └── kustomization.yaml
│
├── helm/
│   └── donekaro/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-local.yaml
│       ├── values-production.yaml
│       └── templates/
│           ├── _helpers.tpl
│           ├── chat-api-deployment.yaml
│           ├── notification-service-deployment.yaml
│           ├── recurring-engine-deployment.yaml
│           └── frontend-deployment.yaml
│
├── scripts/
│   ├── local-setup.sh                  # Minikube + Dapr + Strimzi setup
│   ├── deploy-local.sh                 # Build & deploy to Minikube
│   └── deploy-production.sh            # Deploy to cloud K8s
│
├── docker-compose.yaml                 # Local dev without K8s (Dapr standalone mode)
├── dapr.yaml                           # Dapr multi-app run config (local dev)
└── specs/
    └── 002-cloud-native-event-driven/
        ├── spec.md
        ├── plan.md                     # This file
        ├── research.md
        ├── data-model.md
        ├── quickstart.md
        ├── contracts/
        │   ├── chat-api-openapi.yaml
        │   ├── event-schemas.yaml
        │   └── dapr-subscriptions.yaml
        └── tasks.md
```

**Structure Decision**: Microservices architecture with `/services` containing three independently deployable Python services, `/frontend` for the Next.js app, `/dapr-components` for Dapr YAML configs (split local/production), `/k8s-manifests` for Kubernetes resources using Kustomize overlays, and `/helm` for Helm chart packaging. A `/shared/logging` module provides the mandatory structured JSON logger across all services (installed as a local package or copied during Docker build).

---

## 3. Dapr Component Architecture

### 3.1 State Store: `statestore-postgres`

**Component**: `state.postgresql.v2`
**Backing Store**: PostgreSQL (Neon DB for both local and cloud)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgres
  namespace: donekaro
spec:
  type: state.postgresql.v2
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-credentials
        key: connection-string
    - name: tableName
      value: "dapr_state"
    - name: metadataTableName
      value: "dapr_metadata"
    - name: cleanupIntervalInSeconds
      value: "3600"
    - name: actorStateStore
      value: "false"
  auth:
    secretStore: kubernetes-secrets
```

**State Key Pattern**: `{service-name}||{entity-type}||{id}`
- `chat-api||task||{uuid}` — Task state
- `chat-api||conversation||{uuid}` — Conversation context
- `chat-api||message||{uuid}` — Chat messages
- `notification-service||notification||{uuid}` — Notification records
- `notification-service||push-subscription||{uuid}` — Push subscriptions
- `recurring-engine||recurrence-rule||{uuid}` — Recurrence definitions
- `recurring-engine||job-metadata||{job-name}` — Job registration tracking

**Concurrency**: ETags enforced on all write operations. Clients must read ETag, pass it on save; 409 Conflict on mismatch.

### 3.2 Pub/Sub: `pubsub-kafka`

**Component**: `pubsub.kafka`
**Backing Broker**: Apache Kafka (Strimzi operator for local/Minikube, Redpanda Cloud for production)

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: donekaro
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "{service-name}-group"
    - name: authType
      value: "none"            # Local: none; Production: SASL_SSL
    - name: maxMessageBytes
      value: "1048576"         # 1MB
    - name: consumeRetryInterval
      value: "1000ms"
    - name: version
      value: "3.6.0"
    - name: disableTls
      value: "true"            # Local only; false in production
```

**Topics**:

| Topic | Publisher(s) | Consumer(s) | Purpose |
|-------|-------------|-------------|---------|
| `task-events` | chat-api, recurring-engine | recurring-engine, audit-service* | All task state changes (created, updated, deleted, completed, recurrence-generated) |
| `reminders` | recurring-engine | notification-service | Reminder-fired events (due date approaching, recurring task trigger) |
| `task-updates` | chat-api | notification-service, frontend (via SSE bridge) | Real-time task change propagation for cross-client updates |

*Audit service is P3 and may be a consumer group on `task-events` or a separate service.

**Subscription Configuration** (Declarative):

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: recurring-engine-task-events
spec:
  pubsubname: pubsub-kafka
  topic: task-events
  routes:
    default: /events/task-events
  scopes:
    - recurring-engine
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: notification-reminders
spec:
  pubsubname: pubsub-kafka
  topic: reminders
  routes:
    default: /events/reminders
  scopes:
    - notification-service
---
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: notification-task-updates
spec:
  pubsubname: pubsub-kafka
  topic: task-updates
  routes:
    default: /events/task-updates
  scopes:
    - notification-service
```

### 3.3 Secret Store: `kubernetes-secrets`

**Component**: `secretstores.kubernetes`

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: donekaro
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

**Secrets Managed**:

| Secret Name | Keys | Used By |
|-------------|------|---------|
| `postgres-credentials` | `connection-string` | statestore-postgres component |
| `gemini-credentials` | `api-key` | chat-api (via Dapr Secrets API) |
| `vapid-credentials` | `public-key`, `private-key`, `mailto` | notification-service (Web Push) |
| `auth-credentials` | `jwt-secret` | chat-api (JWT validation) |

**Local Development**: Uses `secretstores.local.file` with a `.secrets.json` file (gitignored).

### 3.4 Jobs API: Dapr Jobs (alpha1)

**Usage**: The recurring-engine registers jobs via the Dapr Jobs HTTP API for:
1. **Recurring task triggers** — Cron-based jobs that fire at scheduled times
2. **Due-date reminders** — One-shot jobs that fire at a calculated reminder time

**Job Registration** (via Dapr HTTP API):

```
PUT http://localhost:3500/v1.0-alpha1/jobs/{job-name}
Content-Type: application/json

{
  "schedule": "@every 24h" | "0 9 * * 1-5",   // Cron or @every syntax
  "repeats": 0,                                 // 0 = indefinite for recurring
  "dueTime": "2026-02-07T16:30:00Z",           // For one-shot reminders
  "data": {
    "taskId": "uuid",
    "type": "recurrence-trigger" | "reminder-fired",
    "userId": "user-uuid"
  }
}
```

**Job Callback**: Dapr calls back to the app at:
```
PUT /job/{job-name}
```
The recurring-engine exposes this endpoint and handles:
- `recurrence-trigger`: Evaluate recurrence rule, generate next instance, publish to `task-events`
- `reminder-fired`: Publish reminder event to `reminders` topic

**Job Naming Convention**: `{type}-{task-id}` (e.g., `recurrence-abc123`, `reminder-def456`)

---

## 4. Event Schema & Communication Flow

### 4.1 CloudEvents Envelope

All events follow the CloudEvents 1.0 specification (Dapr default):

```json
{
  "specversion": "1.0",
  "id": "<uuid>",
  "source": "<service-name>",
  "type": "com.donekaro.<event-type>",
  "datacontenttype": "application/json",
  "time": "<ISO-8601>",
  "traceid": "<W3C-trace-id>",
  "data": { ... }
}
```

### 4.2 Topic: `task-events`

**Event Types and Schemas**:

#### `com.donekaro.task.created`
```json
{
  "eventId": "uuid",
  "eventType": "task-created",
  "taskId": "uuid",
  "userId": "uuid",
  "timestamp": "2026-02-06T10:00:00Z",
  "data": {
    "title": "Buy groceries",
    "description": "Get organic vegetables",
    "status": "pending",
    "priority": "medium",
    "dueDate": "2026-02-07T17:00:00Z",
    "tags": ["shopping"],
    "recurrenceRule": null,
    "etag": "v1-abc123"
  }
}
```

#### `com.donekaro.task.updated`
```json
{
  "eventId": "uuid",
  "eventType": "task-updated",
  "taskId": "uuid",
  "userId": "uuid",
  "timestamp": "2026-02-06T10:05:00Z",
  "data": {
    "before": {
      "title": "Buy groceries",
      "status": "pending"
    },
    "after": {
      "title": "Buy organic groceries",
      "status": "pending"
    },
    "changedFields": ["title"],
    "etag": "v2-def456"
  }
}
```

#### `com.donekaro.task.completed`
```json
{
  "eventId": "uuid",
  "eventType": "task-completed",
  "taskId": "uuid",
  "userId": "uuid",
  "timestamp": "2026-02-06T12:00:00Z",
  "data": {
    "title": "Buy organic groceries",
    "completedAt": "2026-02-06T12:00:00Z",
    "hasRecurrence": false,
    "etag": "v3-ghi789"
  }
}
```

#### `com.donekaro.task.deleted`
```json
{
  "eventId": "uuid",
  "eventType": "task-deleted",
  "taskId": "uuid",
  "userId": "uuid",
  "timestamp": "2026-02-06T12:30:00Z",
  "data": {
    "title": "Buy organic groceries",
    "deletedAt": "2026-02-06T12:30:00Z"
  }
}
```

#### `com.donekaro.task.recurrence-generated`
```json
{
  "eventId": "uuid",
  "eventType": "task-recurrence-generated",
  "taskId": "uuid",
  "parentTaskId": "uuid",
  "userId": "uuid",
  "timestamp": "2026-02-06T12:01:00Z",
  "data": {
    "title": "Team standup",
    "status": "pending",
    "dueDate": "2026-02-07T09:00:00Z",
    "recurrenceRule": {
      "frequency": "weekday",
      "timeOfDay": "09:00",
      "timezone": "UTC"
    },
    "instanceNumber": 42,
    "etag": "v1-new123"
  }
}
```

### 4.3 Topic: `reminders`

#### `com.donekaro.reminder.fired`
```json
{
  "eventId": "uuid",
  "eventType": "reminder-fired",
  "taskId": "uuid",
  "userId": "uuid",
  "timestamp": "2026-02-06T16:30:00Z",
  "data": {
    "taskTitle": "Project proposal",
    "dueDate": "2026-02-06T17:00:00Z",
    "reminderType": "due-date",
    "reminderLevel": "30-minutes-before",
    "notificationChannel": "browser-push"
  }
}
```

#### `com.donekaro.reminder.recurring-trigger`
```json
{
  "eventId": "uuid",
  "eventType": "recurring-trigger",
  "taskId": "uuid",
  "userId": "uuid",
  "timestamp": "2026-02-07T09:00:00Z",
  "data": {
    "taskTitle": "Team standup",
    "recurrenceRule": {
      "frequency": "weekday",
      "timeOfDay": "09:00"
    },
    "triggerReason": "scheduled-job"
  }
}
```

### 4.4 Topic: `task-updates`

#### `com.donekaro.task-update.broadcast`
```json
{
  "eventId": "uuid",
  "eventType": "task-update-broadcast",
  "userId": "uuid",
  "timestamp": "2026-02-06T10:00:00Z",
  "data": {
    "action": "created|updated|completed|deleted",
    "taskId": "uuid",
    "task": {
      "id": "uuid",
      "title": "Buy groceries",
      "status": "pending",
      "priority": "medium",
      "dueDate": "2026-02-07T17:00:00Z",
      "tags": ["shopping"]
    }
  }
}
```

### 4.5 End-to-End Sequence Flow

The canonical data flow through the system follows this path:

```
User Action → Frontend → K8s Ingress → Chat API → Dapr Sidecar → Kafka → Worker Sidecars → Worker Services → Dapr State/Notification
```

#### Master Flow Diagram

```
┌──────────┐     ┌───────────┐     ┌─────────────┐     ┌──────────────────┐
│  Browser  │────▶│  Next.js   │────▶│ K8s Ingress  │────▶│    chat-api       │
│  (User)   │◀───│  Frontend  │◀───│  /api/*      │◀───│    (FastAPI)      │
└──────────┘     └───────────┘     └─────────────┘     └────────┬─────────┘
     ▲                 ▲                                         │
     │                 │                                         │ Dapr Sidecar
     │            SSE Stream                                     ▼
     │           /events/stream                          ┌──────────────────┐
     │                 ▲                                 │  Dapr State API   │──▶ PostgreSQL
     │                 │                                 │  (statestore)    │    (Neon DB)
     │                 │                                 └──────────────────┘
     │                 │                                         │
     │                 │                                         │ Dapr Pub/Sub API
     │                 │                                         ▼
     │                 │                                 ┌──────────────────┐
     │                 │                                 │   Apache Kafka    │
     │                 │                                 │  ┌─────────────┐ │
     │                 │                                 │  │ task-events  │ │
     │                 │                                 │  │ reminders    │ │
     │                 │                                 │  │ task-updates │ │
     │                 │                                 │  └─────────────┘ │
     │                 │                                 └───────┬──────────┘
     │                 │                                    ▼         ▼
     │                 │                          ┌─────────────┐ ┌──────────────┐
     │                 │                          │  recurring-  │ │ notification-│
     │                 │                          │  engine      │ │ service      │
     │                 │                          │  (Worker)    │ │ (Worker)     │
     │                 │                          └──────┬──────┘ └──────┬───────┘
     │                 │                                 │               │
     │                 │                          Dapr Jobs API    Browser Push API
     │                 │                          Dapr State API   Dapr State API
     │                 │                                 │               │
     │                 └─────────────────────────────────┘               │
     └──────────────────────────────────────────────────────────────────┘
                                        Push Notification
```

#### Sequence 1: User Creates Task via Chatbot (Full E2E)

```
  ┌──────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌───────┐  ┌──────────┐  ┌───────────┐
  │ User │  │ Frontend │  │ Ingress │  │chat-api │  │Dapr Side │  │ Kafka │  │recurring │  │notif-svc  │
  └──┬───┘  └────┬─────┘  └────┬────┘  └────┬────┘  └────┬─────┘  └───┬───┘  └────┬─────┘  └─────┬─────┘
     │           │              │            │            │            │            │              │
     │ "Create   │              │            │            │            │            │              │
     │  task:    │              │            │            │            │            │              │
     │  Buy      │ POST /api/  │            │            │            │            │              │
     │  grocer"  │ chat        │            │            │            │            │              │
     ├──────────▶├────────────▶├───────────▶│            │            │            │              │
     │           │              │            │            │            │            │              │
     │           │              │            │ 1. LiteLLM │            │            │              │
     │           │              │            │ intent     │            │            │              │
     │           │              │            │ resolve    │            │            │              │
     │           │              │            │            │            │            │              │
     │           │              │            │ 2. POST    │            │            │              │
     │           │              │            │ state/save │            │            │              │
     │           │              │            ├───────────▶│ Save task  │            │              │
     │           │              │            │            │ to Postgres│            │              │
     │           │              │            │◀───────────┤ (ETag)     │            │              │
     │           │              │            │            │            │            │              │
     │           │              │            │ 3. POST    │            │            │              │
     │           │              │            │ publish/   │            │            │              │
     │           │              │            │ task-events│            │            │              │
     │           │              │            ├───────────▶├───────────▶│            │              │
     │           │              │            │            │            │            │              │
     │           │              │            │ 4. POST    │            │            │              │
     │           │              │            │ publish/   │            │            │              │
     │           │              │            │ task-update│            │            │              │
     │           │              │            ├───────────▶├───────────▶│            │              │
     │           │              │            │            │            │            │              │
     │           │◀─────────────┤◀───────────┤ 5. Return  │            │            │              │
     │◀──────────┤ "Task        │            │ response   │            │            │              │
     │  "Task    │  created"    │            │            │            │            │              │
     │  created" │              │            │            │            │            │              │
     │           │              │            │            │            │            │              │
     │           │              │            │            │        6. task-events  │              │
     │           │              │            │            │        consumed        │              │
     │           │              │            │            │            ├───────────▶│              │
     │           │              │            │            │            │  Has due   │              │
     │           │              │            │            │            │  date?     │              │
     │           │              │            │            │  7. PUT    │  YES →     │              │
     │           │              │            │            │  jobs/     │  register  │              │
     │           │              │            │            │◀───────────┤  reminder  │              │
     │           │              │            │            │            │  job       │              │
     │           │              │            │            │            │            │              │
     │           │              │            │            │        8. task-updates │              │
     │           │              │            │            │        consumed        │              │
     │           │              │            │            │            ├────────────┼─────────────▶│
     │◀──────────┤◀─SSE────────│            │            │            │            │  Push notify │
     │  SSE      │ task-update  │            │            │            │            │  to user     │
     │  event    │ broadcast    │            │            │            │            │              │
```

#### Sequence 2: Recurring Task Completion → Auto-Generate Next Instance

```
  User → Frontend → Ingress → chat-api:
    1. POST /api/chat { message: "Complete 'Team standup'" }
    2. chat-api: LiteLLM → intent: complete_task → resolve task by title

  chat-api → Dapr Sidecar:
    3. GET /v1.0/state/statestore-postgres/task||{taskId}  → read current state + ETag
    4. POST /v1.0/state/statestore-postgres               → save with status=completed, ETag
    5. POST /v1.0/publish/pubsub-kafka/task-events         → task-completed event
    6. POST /v1.0/publish/pubsub-kafka/task-updates        → broadcast for clients

  chat-api → User:
    7. Return "Task 'Team standup' completed. Next instance will be auto-generated."

  Kafka → recurring-engine (async):
    8.  recurring-engine receives task-completed from task-events
    9.  Check task.recurrence_rule_id → non-null → fetch RecurrenceRule from state
    10. GET /v1.0/state/statestore-postgres/recurrence-rule||{ruleId}
    11. Calculate next occurrence: next weekday ≥ tomorrow at 09:00 UTC
    12. Create new Task instance (parent_task_id = original, instance_number++)
    13. POST /v1.0/state/statestore-postgres (transaction):
        - upsert: new task at task||{newTaskId}
        - upsert: updated task-index||{userId} (add new task ID)
        - upsert: updated recurrence-rule (increment instances_generated)
    14. POST /v1.0/publish/pubsub-kafka/task-events → task-recurrence-generated
    15. PUT /v1.0-alpha1/jobs/recurrence-{newTaskId} → register next trigger job

  Kafka → notification-service (async):
    16. notification-service receives task-update broadcast
    17. Send push notification: "Next 'Team standup' scheduled for Mon 9AM"
```

#### Sequence 3: Due-Date Reminder → Push Notification

```
  Phase A — Registration (when task with due date is created):
    1. recurring-engine receives task-created event from task-events topic
    2. Detect: task.due_date = "2026-02-07", task.due_time = "17:00"
    3. Calculate reminder time: 2026-02-07T16:30:00Z (30 min before)
    4. PUT /v1.0-alpha1/jobs/reminder-{taskId}
       Body: { "dueTime": "2026-02-07T16:30:00Z", "data": { taskId, userId, type: "reminder-fired" } }
    5. Save reminder record to state: POST /v1.0/state/statestore-postgres
       Key: reminder||{reminderId}, Value: { status: "scheduled", trigger_time: ... }

  Phase B — Firing (when clock reaches reminder time):
    6.  Dapr scheduler fires → PUT http://recurring-engine:8001/job/reminder-{taskId}
    7.  recurring-engine receives callback with payload
    8.  Idempotency check: GET state job-processed||{taskId}||{instanceId}
        - Already processed? → return 200, skip
    9.  POST /v1.0/publish/pubsub-kafka/reminders → reminder-fired event
    10. Save idempotency marker: POST state with TTL=24h

  Phase C — Delivery (notification-service processes reminder):
    11. notification-service receives reminder-fired from reminders topic
    12. GET /v1.0/state/statestore-postgres/push-sub-index||{userId} → [subscription IDs]
    13. POST /v1.0/state/statestore-postgres/bulk → fetch all PushSubscription objects
    14. For each subscription: POST to Web Push endpoint with payload:
        { title: "Reminder: Project proposal", body: "Due in 30 minutes", url: "/dashboard/tasks/{taskId}" }
    15. Save notification record: POST state notification||{id}
    16. Update reminder status: POST state reminder||{id} → status: "delivered"
    17. Return SUCCESS to Dapr (acknowledges message)

  Failure handling:
    - Push endpoint returns 410 Gone → remove subscription, return SUCCESS
    - Push endpoint returns 5xx → return RETRY (Dapr redelivers after consumeRetryInterval)
    - 3 consecutive failures → return DROP (sent to dead-letter-reminders topic)
```

#### Sequence 4: Real-Time Cross-Client Update via SSE

```
  Client A (mobile browser) creates task → chat-api publishes to task-updates

  Client B (desktop browser) has open SSE connection:
    1. Client B: EventSource connected to GET /events/stream?userId={userId}
    2. chat-api pod receives task-update-broadcast from Kafka via Dapr subscription
    3. chat-api: Route POST /events/task-updates handler:
       - Extract userId from event data
       - Look up sse_connections[userId] → list of asyncio.Queue objects
       - Push event data to each Queue
    4. SSE generator in Client B's connection reads from Queue
    5. Yields: "id: {eventId}\nevent: task-update\ndata: {json}\n\n"
    6. Client B's EventSource fires 'task-update' event
    7. TanStack Query invalidates task list cache → UI re-renders with new task

  Reconnection:
    - If SSE connection drops, EventSource auto-reconnects
    - Last-Event-ID header sent → chat-api can skip already-seen events
    - On pod restart: client reconnects to new pod, polls /tasks for latest state
```

#### Sequence 5: Graceful Degradation (Notification Service Down)

```
  1. User creates task via chatbot → chat-api processes normally
  2. chat-api → Dapr State: Save task ✓
  3. chat-api → Dapr Pub/Sub: Publish to task-events ✓ (Kafka accepts regardless)
  4. chat-api → Dapr Pub/Sub: Publish to task-updates ✓ (Kafka accepts regardless)
  5. chat-api → User: "Task created successfully" ✓ (FR-009 satisfied)

  Meanwhile:
  6. notification-service pods are down (CrashLoopBackOff)
  7. Kafka retains events in reminders and task-updates topics (retention: 7 days / 1 day)
  8. Events accumulate with consumer group offset tracking

  Recovery:
  9.  notification-service pods restart
  10. Kafka consumer group resumes from last committed offset
  11. notification-service processes backlog of events
  12. All missed notifications delivered (SC-006: 100% event capture)
```

---

## 5. Frontend Integration Strategy

### 5.1 Dapr Service Invocation (Frontend → Backend)

The Next.js frontend calls the chat-api through Dapr Service Invocation instead of direct HTTP:

**Local Development**: Frontend calls chat-api at `http://localhost:{dapr-http-port}/v1.0/invoke/chat-api/method/{endpoint}`

**Kubernetes**: Frontend pod has its own Dapr sidecar; calls go through:
```
http://localhost:3500/v1.0/invoke/chat-api/method/chat
```

**Alternative (simpler)**: Use a Kubernetes Ingress/Gateway to route `/api/*` to chat-api service, keeping the frontend unaware of Dapr. This is the recommended approach for the frontend since the Next.js app runs in the browser and cannot use Dapr sidecars directly.

**Decision**: Frontend calls an API gateway (Kubernetes Ingress) that routes to chat-api. The chat-api internally uses Dapr for all infrastructure. This preserves the frontend's simplicity while the backend is fully Dapr-native.

### 5.2 Real-Time Updates (SSE Bridge)

The chat-api exposes an SSE endpoint that bridges Kafka `task-updates` events to the browser:

```
GET /events/stream?userId={userId}
Accept: text/event-stream
Authorization: Bearer {token}
```

The chat-api subscribes to `task-updates` via Dapr Pub/Sub and maintains an in-memory map of SSE connections per user. When a `task-update-broadcast` event arrives for a user, it's pushed to all their connected SSE clients.

---

## 6. Shared Infrastructure

### 6.1 Structured JSON Logging Module

All three services import a shared logging configuration:

```python
# shared/logging/config.py
import json, logging, sys
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "unknown"),
            "trace_id": getattr(record, "trace_id", ""),
            "message": record.getMessage(),
        })

def setup_logging(service_name: str, level: str = "INFO"):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    logger = logging.getLogger(service_name)
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level))
    return logger
```

### 6.2 Dapr HTTP Client Pattern

Each service uses a thin HTTP wrapper to call Dapr sidecar APIs:

```python
# Template for each service's dapr_client.py
import httpx

DAPR_HTTP_PORT = int(os.environ.get("DAPR_HTTP_PORT", "3500"))
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

async def publish_event(pubsub: str, topic: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{DAPR_BASE_URL}/v1.0/publish/{pubsub}/{topic}",
            json=data
        )

async def get_state(store: str, key: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DAPR_BASE_URL}/v1.0/state/{store}/{key}")
        return resp.json()

async def save_state(store: str, items: list[dict]):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{DAPR_BASE_URL}/v1.0/state/{store}",
            json=items
        )

async def get_secret(store: str, key: str) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DAPR_BASE_URL}/v1.0/secrets/{store}/{key}")
        return resp.json()
```

---

## 7. Infrastructure & Deployment Strategy

### 7.1 Containerization — Multi-Stage Dockerfiles

All three Python services use an identical multi-stage Dockerfile pattern optimized for small image size and fast builds.

#### Python Service Dockerfile (chat-api, notification-service, recurring-engine)

```dockerfile
# ============================================================
# Stage 1: Builder — install dependencies in a venv
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build tools for any native extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libffi-dev && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy shared logging module
COPY --from=shared-logging . /build/shared/logging/

# ============================================================
# Stage 2: Runtime — minimal image with only runtime deps
# ============================================================
FROM python:3.11-slim AS runtime

# Security: run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY app/ ./app/
COPY --from=builder /build/shared/logging/ ./shared/logging/

# Metadata
LABEL org.opencontainers.image.source="https://github.com/donekaro/todo-phase-5"
LABEL org.opencontainers.image.description="DoneKaro {service-name}"

# Switch to non-root
USER appuser

# Expose port (8000 for chat-api, 8001 for workers)
EXPOSE 8000

# Health check (Dapr sidecar handles K8s probes, this is a fallback)
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

**Per-Service Customizations**:

| Service | Port | Workers | CMD Override |
|---------|------|---------|-------------|
| chat-api | 8000 | 2-4 (CPU bound: AI inference) | `--workers 4` in production |
| notification-service | 8001 | 1 (I/O bound: push delivery) | `--port 8001` |
| recurring-engine | 8002 | 1 (event-driven, low throughput) | `--port 8002` |

**Build Optimization**:
- `requirements.txt` copied before app code → Docker caches the pip install layer
- Multi-stage build → final image has no gcc, build tools, or pip cache
- `python:3.11-slim` base → ~150MB image vs ~900MB for full Python
- Non-root user → K8s PodSecurityPolicy compliant

#### Frontend Dockerfile (Next.js)

```dockerfile
# ============================================================
# Stage 1: Dependencies
# ============================================================
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev

# ============================================================
# Stage 2: Builder
# ============================================================
FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time environment variables
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm run build

# ============================================================
# Stage 3: Runtime (standalone output)
# ============================================================
FROM node:20-alpine AS runtime
WORKDIR /app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

USER appuser
EXPOSE 3000
ENV PORT=3000 HOSTNAME="0.0.0.0"
CMD ["node", "server.js"]
```

**Frontend Build Notes**:
- Next.js `output: "standalone"` in `next.config.ts` produces a self-contained Node.js server
- Final image is ~80MB (Alpine + standalone output)
- `NEXT_PUBLIC_API_URL` injected at build time; points to K8s Ingress URL

### 7.2 Kubernetes Orchestration — Helm Charts

#### Chart Structure

```text
helm/donekaro/
├── Chart.yaml                      # Chart metadata + dependencies
├── values.yaml                     # Default values (local dev)
├── values-local.yaml               # Minikube overrides
├── values-production.yaml          # AKS/GKE overrides
└── templates/
    ├── _helpers.tpl                # Template helpers (labels, names, annotations)
    ├── namespace.yaml
    ├── chat-api/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── hpa.yaml
    ├── notification-service/
    │   ├── deployment.yaml
    │   └── service.yaml
    ├── recurring-engine/
    │   ├── deployment.yaml
    │   └── service.yaml
    ├── frontend/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── ingress.yaml
    ├── dapr-components/
    │   ├── statestore.yaml
    │   ├── pubsub.yaml
    │   ├── secretstore.yaml
    │   └── subscriptions.yaml
    └── infrastructure/
        ├── kafka-cluster.yaml      # Strimzi CRD (conditional)
        └── kafka-topics.yaml
```

#### Helm values.yaml (Default / Shared)

```yaml
global:
  namespace: donekaro
  imageRegistry: ""                 # Empty for local; set for ACR/GCR
  imagePullPolicy: IfNotPresent

chatApi:
  replicaCount: 1
  image:
    repository: donekaro/chat-api
    tag: latest
  port: 8000
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 512Mi
  dapr:
    enabled: true
    appId: chat-api
    appPort: 8000
    logLevel: info
  hpa:
    enabled: false
    minReplicas: 1
    maxReplicas: 5
    targetCPUUtilization: 70

notificationService:
  replicaCount: 1
  image:
    repository: donekaro/notification-service
    tag: latest
  port: 8001
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi
  dapr:
    enabled: true
    appId: notification-service
    appPort: 8001
    logLevel: info

recurringEngine:
  replicaCount: 1
  image:
    repository: donekaro/recurring-engine
    tag: latest
  port: 8002
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi
  dapr:
    enabled: true
    appId: recurring-engine
    appPort: 8002
    logLevel: info

frontend:
  replicaCount: 1
  image:
    repository: donekaro/frontend
    tag: latest
  port: 3000
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 256Mi
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: donekaro.local
        paths:
          - path: /
            pathType: Prefix
            service: frontend
          - path: /api
            pathType: Prefix
            service: chat-api

kafka:
  enabled: true                     # Set false for Redpanda Cloud
  replicas: 1
  storage: ephemeral

dapr:
  statestore:
    name: statestore-postgres
    type: state.postgresql.v2
  pubsub:
    name: pubsub-kafka
    type: pubsub.kafka
    brokers: kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
  secretstore:
    name: kubernetes-secrets
    type: secretstores.kubernetes
```

#### Deployment Template (chat-api example)

```yaml
# templates/chat-api/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "donekaro.chatApi.name" . }}
  namespace: {{ .Values.global.namespace }}
  labels:
    {{- include "donekaro.labels" . | nindent 4 }}
    app.kubernetes.io/component: chat-api
spec:
  replicas: {{ .Values.chatApi.replicaCount }}
  selector:
    matchLabels:
      app: chat-api
  template:
    metadata:
      labels:
        app: chat-api
      annotations:
        dapr.io/enabled: "{{ .Values.chatApi.dapr.enabled }}"
        dapr.io/app-id: "{{ .Values.chatApi.dapr.appId }}"
        dapr.io/app-port: "{{ .Values.chatApi.dapr.appPort }}"
        dapr.io/log-level: "{{ .Values.chatApi.dapr.logLevel }}"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
        - name: chat-api
          image: "{{ .Values.global.imageRegistry }}{{ .Values.chatApi.image.repository }}:{{ .Values.chatApi.image.tag }}"
          imagePullPolicy: {{ .Values.global.imagePullPolicy }}
          ports:
            - containerPort: {{ .Values.chatApi.port }}
              protocol: TCP
          env:
            - name: SERVICE_NAME
              value: chat-api
            - name: LOG_LEVEL
              value: INFO
            - name: DAPR_HTTP_PORT
              value: "3500"
          resources:
            {{- toYaml .Values.chatApi.resources | nindent 12 }}
          livenessProbe:
            httpGet:
              path: /health
              port: {{ .Values.chatApi.port }}
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: {{ .Values.chatApi.port }}
            initialDelaySeconds: 5
            periodSeconds: 10
```

#### values-production.yaml Overrides

```yaml
global:
  imageRegistry: "donekaro.azurecr.io/"     # ACR registry
  imagePullPolicy: Always

chatApi:
  replicaCount: 2
  image:
    tag: "1.0.0"                             # Pinned version
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 1Gi
  hpa:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilization: 60

notificationService:
  replicaCount: 2
  resources:
    requests:
      cpu: 250m
      memory: 256Mi

recurringEngine:
  replicaCount: 1                            # Single instance (idempotent callbacks)

kafka:
  enabled: false                             # Using Redpanda Cloud in production

dapr:
  pubsub:
    brokers: ""                              # From Kubernetes Secret
    authType: password
    saslMechanism: SCRAM-SHA-256
```

### 7.3 CI/CD — GitHub Actions Workflow

#### Workflow: Build, Test, and Deploy

```yaml
# .github/workflows/deploy.yaml
name: Build, Test & Deploy

on:
  push:
    branches: [main]
    paths:
      - 'services/**'
      - 'frontend/**'
      - 'shared/**'
      - 'helm/**'
  pull_request:
    branches: [main]

env:
  REGISTRY: donekaro.azurecr.io              # ACR for Azure; gcr.io/$PROJECT for GCP
  DAPR_VERSION: "1.14"

jobs:
  # ─────────────────────────────────────────────────
  # Job 1: Lint & Unit Test (all services in parallel)
  # ─────────────────────────────────────────────────
  lint-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [chat-api, notification-service, recurring-engine]
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          cd services/${{ matrix.service }}
          pip install -r requirements.txt
          pip install ruff pytest pytest-asyncio pytest-cov

      - name: Lint with ruff
        run: ruff check services/${{ matrix.service }}/

      - name: Unit tests
        run: |
          cd services/${{ matrix.service }}
          pytest tests/unit/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.service }}
          path: services/${{ matrix.service }}/coverage.xml

  # ─────────────────────────────────────────────────
  # Job 2: Frontend lint & build
  # ─────────────────────────────────────────────────
  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install & build
        run: |
          cd frontend
          npm ci
          npm run lint
          npm run build

  # ─────────────────────────────────────────────────
  # Job 3: Build & push Docker images
  # ─────────────────────────────────────────────────
  build-images:
    needs: [lint-test, frontend-build]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include:
          - service: chat-api
            context: services/chat-api
          - service: notification-service
            context: services/notification-service
          - service: recurring-engine
            context: services/recurring-engine
          - service: frontend
            context: frontend
    steps:
      - uses: actions/checkout@v4

      - name: Log in to container registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ secrets.ACR_USERNAME }}
          password: ${{ secrets.ACR_PASSWORD }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.context }}
          push: true
          tags: |
            ${{ env.REGISTRY }}/donekaro/${{ matrix.service }}:${{ github.sha }}
            ${{ env.REGISTRY }}/donekaro/${{ matrix.service }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ─────────────────────────────────────────────────
  # Job 4: Integration test with Dapr
  # ─────────────────────────────────────────────────
  integration-test:
    needs: [build-images]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Dapr CLI
        run: |
          wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
          dapr init

      - name: Run integration tests
        run: |
          # Start services with Dapr multi-app run
          dapr run -f dapr.yaml &
          sleep 15
          # Run integration test suite
          cd services/chat-api
          pip install -r requirements.txt
          pytest tests/integration/ -v --timeout=60

  # ─────────────────────────────────────────────────
  # Job 5: Deploy to AKS (production)
  # ─────────────────────────────────────────────────
  deploy-production:
    needs: [integration-test]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production                   # Requires manual approval
    steps:
      - uses: actions/checkout@v4

      - name: Azure login
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Set AKS context
        uses: azure/aks-set-context@v4
        with:
          cluster-name: donekaro-aks
          resource-group: donekaro-rg

      - name: Install Helm
        uses: azure/setup-helm@v4

      - name: Deploy with Helm
        run: |
          helm upgrade --install donekaro helm/donekaro/ \
            --namespace donekaro \
            --create-namespace \
            -f helm/donekaro/values-production.yaml \
            --set chatApi.image.tag=${{ github.sha }} \
            --set notificationService.image.tag=${{ github.sha }} \
            --set recurringEngine.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            --wait --timeout 5m

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/chat-api -n donekaro --timeout=120s
          kubectl rollout status deployment/notification-service -n donekaro --timeout=120s
          kubectl rollout status deployment/recurring-engine -n donekaro --timeout=120s
          kubectl rollout status deployment/frontend -n donekaro --timeout=120s

      - name: Smoke test
        run: |
          INGRESS_IP=$(kubectl get ingress -n donekaro -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')
          curl -f http://$INGRESS_IP/api/health || exit 1
```

#### GKE Variant

For Google Cloud deployment, replace the deploy job with:

```yaml
  deploy-gke:
    steps:
      - uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GCP_CREDENTIALS }}

      - uses: google-github-actions/get-gke-credentials@v2
        with:
          cluster_name: donekaro-gke
          location: us-central1

      - name: Deploy with Helm
        run: |
          helm upgrade --install donekaro helm/donekaro/ \
            --namespace donekaro \
            -f helm/donekaro/values-production.yaml \
            --set global.imageRegistry="gcr.io/${{ secrets.GCP_PROJECT }}/" \
            --set chatApi.image.tag=${{ github.sha }} \
            # ... same pattern
```

#### CI/CD Pipeline Flow

```
PR opened → lint-test (3 services parallel) + frontend-build
          ↓
Merge to main → build-images (4 images parallel, push to ACR/GCR)
              ↓
              → integration-test (Dapr + Docker Compose)
              ↓
              → deploy-production (Helm upgrade, manual approval gate)
              ↓
              → smoke test (health check via Ingress IP)
```

### 7.4 Local Development (Minikube)

1. **Minikube** with Dapr sidecar injector installed
2. **Strimzi Kafka operator** deployed in `kafka` namespace
3. **Dapr components** applied from `dapr-components/local/`
4. **Services** built as Docker images, loaded into Minikube registry
5. **Kustomize** overlays for local patches (resource limits, replicas=1)
6. Deploy: `helm install donekaro helm/donekaro/ -f helm/donekaro/values-local.yaml -n donekaro`

### 7.5 Docker Compose (Quick Local Dev)

For developers who don't need full Kubernetes, a `docker-compose.yaml` runs:
- 3 services with Dapr sidecars (standalone mode)
- Kafka (single-broker via Redpanda)
- PostgreSQL (local instance for offline dev)
- Dapr placement service
- Frontend with hot-reload

---

## 8. Migration Strategy from Phase 2

### 8.1 Extraction & Wrapping Strategy

The migration follows a **Strangler Fig** pattern: Phase 2 logic is extracted module-by-module, wrapped in Dapr-aware service layers, and deployed as independent services. No big-bang rewrite.

#### Step-by-Step Extraction Process

**Step 1: Extract chatbot core → chat-api service**

Phase 2 Source (`todo-phase-2/backend/app/`):
```
chatbot/runner.py    → LiteLLM agent loop, tool calling
chatbot/tools.py     → list_tasks, add_task, complete_task, update_task, delete_task, find_task_by_title
routes/chat.py       → POST /api/{userId}/chat endpoint
models/task.py       → Task SQLModel + Pydantic schemas
models/conversation.py → Conversation, Message SQLModel
auth/jwt_bearer.py   → JWT Bearer validation
config.py            → Pydantic Settings (env vars)
database.py          → SQLModel async session (get_session)
```

**Wrapping in Dapr**:

| Phase 2 Layer | Wrapping Required | Phase 5 Replacement |
|---------------|-------------------|---------------------|
| `database.py` (SQLModel session) | **Full replace** | `services/state_service.py` (Dapr State HTTP calls) |
| `tools.py` (direct DB queries) | **Rewrite internals** | Keep function signatures; replace body with `state_service` + `pubsub_service` calls |
| `runner.py` (LiteLLM agent) | **Copy with minimal changes** | Same LiteLLM flow; tools now call Dapr-wrapped services |
| `routes/chat.py` | **Adapt** | Remove `{userId}` path param (extract from JWT); add conversation_id handling |
| `models/task.py` | **Strip SQLModel** | Keep Pydantic schemas; remove `SQLModel` base class, `table=True`, `Field(sa_column=...)` |
| `auth/jwt_bearer.py` | **Wrap as middleware** | Convert from route dependency to FastAPI middleware |
| `config.py` | **Replace env vars** | Use Dapr Secrets API to fetch credentials at startup |

**Concrete example — wrapping `tools.py` `add_task()`**:

```python
# Phase 2 (direct DB)
async def add_task(title: str, user_id: str, session: AsyncSession) -> str:
    task = Task(title=title, user_id=user_id)
    session.add(task)
    await session.commit()
    return f"Task '{title}' created with ID {task.id}"

# Phase 5 (Dapr-wrapped)
async def add_task(title: str, user_id: str) -> str:
    task = Task(title=title, user_id=user_id)
    # Save via Dapr State API
    await state_service.save_task(task)
    # Publish event via Dapr Pub/Sub
    await pubsub_service.publish_task_event("task-created", task)
    # Publish broadcast for real-time clients
    await pubsub_service.publish_task_update("created", task)
    return f"Task '{title}' created with ID {task.id}"
```

**Key change**: The function signature stays the same (LiteLLM tool interface unchanged), but the `session` parameter is removed and replaced by service calls to Dapr APIs. No Kafka imports, no psycopg2, no SQLModel — only `httpx` calls to `localhost:3500`.

**Step 2: Extract notification logic → notification-service**

Phase 2 Source:
```
services/notification.py → create_notification(), send to user
services/email.py        → Resend API email delivery
services/fcm.py          → Firebase Cloud Messaging
services/webpush.py      → Web Push API
models/notification.py   → Notification SQLModel
models/push_subscription.py → PushSubscription SQLModel
models/fcm_token.py      → FCM token model
routes/notifications.py  → GET/PUT/DELETE notification endpoints
routes/push.py           → Push subscribe/unsubscribe
routes/fcm.py            → FCM token registration
```

**Wrapping in Dapr**:

| Phase 2 Component | Phase 5 Action |
|-------------------|----------------|
| `services/notification.py` | Rewrite as event handler (consumes from `reminders` topic instead of being called directly) |
| `services/webpush.py` | **Keep as-is** (uses `pywebpush` library — this is a notification delivery library, not infrastructure) |
| `services/email.py` | **Drop** (email is out of scope for Phase 5) |
| `services/fcm.py` | **Drop** (FCM replaced by browser Push API only) |
| `models/notification.py` | Strip SQLModel → Pydantic only; store via Dapr State |
| `models/push_subscription.py` | Strip SQLModel → Pydantic only |
| `models/fcm_token.py` | **Drop** (no FCM in Phase 5) |
| `routes/notifications.py` | Move to chat-api (user-facing queries) OR notification-service (if separate API needed) |

**The notification-service becomes event-driven**:
```python
# Phase 2: Called synchronously from task routes
await notification_service.create_notification(user_id, title, message, type)

# Phase 5: Triggered by Kafka event consumption
@app.post("/events/reminder-fired")
async def handle_reminder(request: Request):
    event = await request.json()
    # Extract notification details from event
    user_id = event["data"]["userId"]
    task_title = event["data"]["data"]["taskTitle"]
    # Deliver notification
    subscriptions = await state_service.get_push_subscriptions(user_id)
    for sub in subscriptions:
        await push_service.send_notification(sub, title=f"Reminder: {task_title}", ...)
    return {"status": "SUCCESS"}
```

**Step 3: Build recurring-engine (NEW — no Phase 2 equivalent)**

Phase 2 has `services/scheduler.py` using APScheduler, but it's fundamentally different:
```python
# Phase 2: In-process APScheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(check_deadlines, 'interval', minutes=30)
scheduler.start()  # Runs inside the monolith process
```

Phase 5 recurring-engine is built from scratch:
- Event-driven (subscribes to `task-events`)
- Uses Dapr Jobs API for scheduling (not APScheduler)
- Generates new task instances (new capability)
- No Phase 2 code is reused for this service

### 8.2 Frontend Migration — Dapr Service Invocation

#### Phase 2 Frontend Architecture (Current)

```typescript
// lib/api.ts (Phase 2)
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi(path: string, options: RequestInit = {}) {
    const token = await getAuthToken();
    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
            ...options.headers,
        },
    });
    if (!response.ok) throw new ApiError(response.status, await response.text());
    return response.json();
}

// Usage:
const tasks = await fetchApi("/api/tasks");
const chatResponse = await fetchApi("/api/{userId}/chat", { method: "POST", body: JSON.stringify({ message }) });
```

#### Phase 5 Frontend Architecture (Migrated)

The frontend does NOT call Dapr directly. The browser cannot run a Dapr sidecar. Instead:

**Architecture Decision**: Frontend → Kubernetes Ingress → chat-api (with Dapr sidecar)

```
Browser → https://donekaro.app/api/* → K8s Ingress → chat-api Service → chat-api Pod [Dapr sidecar]
Browser → https://donekaro.app/*     → K8s Ingress → frontend Service → frontend Pod
```

**Ingress Configuration** (in Helm chart):
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: donekaro-ingress
  namespace: donekaro
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$2
spec:
  ingressClassName: nginx
  rules:
    - host: donekaro.app
      http:
        paths:
          # API routes → chat-api service
          - path: /api(/|$)(.*)
            pathType: ImplementationSpecific
            backend:
              service:
                name: chat-api
                port:
                  number: 8000
          # Frontend routes → frontend service
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
```

**Frontend api.ts Changes (Phase 2 → Phase 5)**:

```typescript
// lib/api.ts (Phase 5)
// The API URL now points to the Ingress, which routes /api/* to chat-api
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";  // Same origin in production

async function fetchApi(path: string, options: RequestInit = {}) {
    const token = await getAuthToken();
    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
            ...options.headers,
        },
    });
    if (!response.ok) throw new ApiError(response.status, await response.text());
    return response.json();
}

// Usage (API paths change slightly):
const tasks = await fetchApi("/api/tasks");           // Same pattern
const chatResponse = await fetchApi("/api/chat", {    // Removed {userId} — extracted from JWT
    method: "POST",
    body: JSON.stringify({ message }),
});
```

**Key Frontend Changes**:

| Change | Phase 2 | Phase 5 | Reason |
|--------|---------|---------|--------|
| API base URL | `http://localhost:8000` | Same-origin (`""`) or Ingress URL | Routed through K8s Ingress |
| Chat endpoint | `POST /api/{userId}/chat` | `POST /api/chat` | userId extracted from JWT server-side |
| Real-time updates | Polling / manual refresh | SSE via `EventSource` | Real-time via Kafka → SSE bridge |
| Push notifications | FCM + Web Push (mixed) | Browser Push API only | Simplified; FCM dropped |
| Task refresh | TanStack Query refetch on mutation | TanStack Query invalidated by SSE events | Instant cross-client updates |

**New: SSE Client Integration**:

```typescript
// lib/sse-client.ts (NEW)
import { useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";

export function useTaskUpdates(userId: string) {
    const queryClient = useQueryClient();

    useEffect(() => {
        const source = new EventSource(`/api/events/stream?userId=${userId}`);

        source.addEventListener("task-update", (event) => {
            const data = JSON.parse(event.data);

            // Invalidate TanStack Query cache to trigger re-fetch
            queryClient.invalidateQueries({ queryKey: ["tasks"] });

            // Optionally update cache optimistically
            if (data.action === "created" && data.task) {
                queryClient.setQueryData(["tasks"], (old: Task[] | undefined) =>
                    old ? [data.task, ...old] : [data.task]
                );
            }
        });

        source.onerror = () => {
            console.warn("SSE connection error, auto-reconnecting...");
        };

        return () => source.close();
    }, [userId, queryClient]);
}

// Usage in dashboard layout:
function DashboardLayout({ children }: { children: React.ReactNode }) {
    const { user } = useAuth();
    useTaskUpdates(user.id);  // Enables real-time updates globally
    return <>{children}</>;
}
```

**Next.js Server-Side Dapr Invocation (API Routes)**:

For Next.js API routes that run server-side (in the frontend pod), Dapr Service Invocation is available because the frontend pod has its own Dapr sidecar:

```typescript
// app/api/user/route.ts (runs server-side in frontend pod)
export async function GET(request: Request) {
    // Frontend's Dapr sidecar can invoke chat-api via Service Invocation
    const response = await fetch(
        "http://localhost:3500/v1.0/invoke/chat-api/method/tasks",
        {
            headers: {
                "dapr-app-id": "chat-api",
                "Authorization": request.headers.get("Authorization") || "",
            },
        }
    );
    return Response.json(await response.json());
}
```

**Decision**: Use Ingress routing for client-side calls (browser → Ingress → chat-api) and Dapr Service Invocation for server-side calls (Next.js API routes → Dapr sidecar → chat-api). This gives the best of both worlds.

### 8.3 What Gets Migrated (Complete Mapping)

| Phase 2 Component | Phase 5 Destination | Migration Type |
|-------------------|---------------------|----------------|
| `backend/app/chatbot/runner.py` | `services/chat-api/app/chatbot/runner.py` | **Copy + adapt** (tools call Dapr services) |
| `backend/app/chatbot/tools.py` | `services/chat-api/app/chatbot/tools.py` | **Rewrite internals** (same signatures, Dapr body) |
| `backend/app/models/task.py` | `services/chat-api/app/models/task.py` | **Strip SQLModel** → Pydantic only; add recurrence fields |
| `backend/app/models/conversation.py` | `services/chat-api/app/models/conversation.py` | **Strip SQLModel** → Pydantic; inline messages |
| `backend/app/models/notification.py` | `services/notification-service/app/models/notification.py` | **Strip SQLModel** → Pydantic |
| `backend/app/routes/chat.py` | `services/chat-api/app/routes/chat.py` | **Adapt** (remove {userId} path, add event publish) |
| `backend/app/routes/tasks.py` | `services/chat-api/app/routes/tasks.py` | **Rewrite** (Dapr State API, event publishing) |
| `backend/app/routes/health.py` | All services `/health` | **Standardize** (add Dapr connectivity check) |
| `backend/app/services/scheduler.py` | `services/recurring-engine/` | **Full rewrite** (APScheduler → Dapr Jobs) |
| `backend/app/services/notification.py` | `services/notification-service/handlers/` | **Rewrite** (sync call → event consumer) |
| `backend/app/services/webpush.py` | `services/notification-service/services/push_service.py` | **Copy + adapt** (pywebpush stays) |
| `backend/app/auth/jwt_bearer.py` | `services/chat-api/app/middleware/auth.py` | **Wrap** (dependency → middleware) |
| `backend/app/config.py` | `services/chat-api/app/config.py` | **Replace** (env vars → Dapr Secrets API) |
| `backend/app/database.py` | **DROPPED** | Replaced by `state_service.py` |
| `frontend/lib/api.ts` | `frontend/lib/api.ts` | **Minor update** (URL + endpoint changes) |
| `frontend/components/chat-widget.tsx` | `frontend/components/chat-widget.tsx` | **Copy** (minimal changes) |
| N/A (new) | `frontend/lib/sse-client.ts` | **New** (SSE for real-time) |
| N/A (new) | `services/recurring-engine/*` | **New** (entire service) |
| N/A (new) | `shared/logging/*` | **New** (JSON logging module) |
| N/A (new) | `dapr-components/*` | **New** (Dapr YAML configs) |
| N/A (new) | `k8s-manifests/*` and `helm/*` | **New** (K8s deployment) |
| N/A (new) | `.github/workflows/deploy.yaml` | **New** (CI/CD pipeline) |

### 8.4 What Gets Dropped

| Phase 2 Component | Reason |
|-------------------|--------|
| `SQLModel` / SQLAlchemy | Replaced by Dapr State API (Constitution III) |
| `psycopg2` / `asyncpg` | No direct DB drivers (Constitution III) |
| `APScheduler` | Replaced by Dapr Jobs API (Constitution IV) |
| `firebase-admin` | FCM dropped; browser Push API only |
| `services/email.py` | Email notifications out of scope |
| `services/fcm.py` | FCM replaced by Web Push |
| `models/fcm_token.py` | No FCM tokens |
| `routes/fcm.py` | No FCM endpoints |
| `database.py` | No direct database access |
| `migrations/` | No SQL migrations (Dapr manages state table) |
| `capacitor.config.ts` | No mobile app (web-only in Phase 5) |

### 8.5 Migration Order (Recommended)

```
Phase A: Foundation (Weeks 1-2)
  1. Scaffold services/ directory structure
  2. Create shared logging module
  3. Create Dapr client wrapper for each service
  4. Set up Dapr components (local dev)
  5. Write Dockerfiles for all services
  6. Set up Helm chart skeleton

Phase B: chat-api (Weeks 2-3)
  7. Migrate models (strip SQLModel → Pydantic)
  8. Implement state_service.py + pubsub_service.py
  9. Migrate chatbot/runner.py + tools.py (wrap with Dapr calls)
  10. Migrate routes/chat.py (adapt for Dapr)
  11. Add SSE bridge endpoint
  12. Implement JWT middleware

Phase C: recurring-engine (Weeks 3-4)
  13. Build recurrence_service.py (rule evaluation, next-instance calculation)
  14. Build job_service.py (Dapr Jobs registration/cancellation)
  15. Build event handlers (task-completed → generate next instance)
  16. Build job callback handler (scheduled trigger → publish reminder)

Phase D: notification-service (Week 4)
  17. Build reminder event handler
  18. Migrate Web Push delivery (from Phase 2 webpush.py)
  19. Build push subscription management via Dapr State

Phase E: Frontend (Week 4-5)
  20. Update api.ts (URL changes, endpoint changes)
  21. Add SSE client (sse-client.ts)
  22. Integrate useTaskUpdates hook into dashboard layout
  23. Remove FCM/Capacitor code

Phase F: Infrastructure (Week 5)
  24. Finalize Helm charts
  25. Set up GitHub Actions CI/CD
  26. Deploy to Minikube (integration test)
  27. Deploy to production (AKS/GKE)
```

---

## Complexity Tracking

> No constitution violations detected. All design decisions align with the 7 core principles.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| 3 services (not 2, not 4) | Constitution mandates exactly 3 | Principle I defines chat-api, notification-service, recurring-engine |
| Dapr HTTP API (not SDK) | Use httpx to call Dapr sidecar HTTP endpoints | Simpler than Dapr Python SDK, avoids SDK version coupling, Constitution III compliant |
| SSE over WebSocket | Server-Sent Events for real-time updates | Simpler, unidirectional (server→client), sufficient for task update broadcasts |
| Kustomize + Helm | Kustomize for environment overlays, Helm for packaging | Kustomize for fine-grained patches; Helm for distribution/versioning |
| Strimzi (local) / Redpanda (cloud) | Different Kafka implementations per environment | Strimzi is free for local K8s; Redpanda Cloud reduces ops burden in production |

---

## Risks and Mitigations

1. **Dapr Jobs API is alpha1**: May have breaking changes or limitations. **Mitigation**: Abstract job registration behind a service layer; fallback to Dapr Bindings (cron) if Jobs API is insufficient.

2. **Event ordering in Kafka**: Task events may arrive out of order across partitions. **Mitigation**: Use `taskId` as the Kafka partition key to ensure per-task ordering. Include monotonic sequence numbers in events.

3. **SSE connection scalability**: In-memory SSE connection map in chat-api won't survive pod restarts. **Mitigation**: Clients auto-reconnect with `Last-Event-ID`; stateless SSE with Kafka consumer group per pod instance.

---

## Follow-Ups

- Generate `research.md` resolving Dapr Jobs API alpha1 specifics, Strimzi vs Redpanda trade-offs, and SSE scaling patterns (Phase 0)
- Generate `data-model.md` with full entity definitions and Dapr state key mappings (Phase 1)
- Generate API contracts in `contracts/` directory (Phase 1)
- Generate `quickstart.md` for local development setup (Phase 1)
- Run `/sp.tasks` to generate implementation task list (Phase 2 — separate command)
