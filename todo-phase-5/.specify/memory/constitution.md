<!--
  Sync Impact Report
  ===================
  Version change: N/A (initial) → 1.0.0
  Modified principles: N/A (initial ratification)
  Added sections:
    - Core Principles (7 principles)
    - Tech Stack Constraints
    - Development Workflow (Agentic Rules)
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no changes needed (generic)
    - .specify/templates/spec-template.md ✅ no changes needed (generic)
    - .specify/templates/tasks-template.md ✅ no changes needed (generic)
  Follow-up TODOs: None
-->

# DoneKaro Phase V Constitution

## Core Principles

### I. Cloud-Native Microservices

The application MUST be decomposed into exactly three primary services:

- **chat-api** — Handles user-facing chat interactions and AI orchestration.
- **notification-service** — Delivers notifications triggered by system events.
- **recurring-engine** — Manages recurring task scheduling and execution.

Each service MUST be independently deployable, independently scalable,
and packaged as a single container image with its own Dockerfile.
No service may share a runtime process with another service.

### II. Event-Driven Architecture (EDA)

Services MUST NOT communicate directly via synchronous HTTP calls
or any form of request-response coupling between services.

All inter-service logic MUST be triggered by events published to
and consumed from Apache Kafka topics. Each event MUST have a
well-defined schema. Services MUST be eventual-consistency aware;
no service may assume immediate availability of data produced by
another service.

**Rationale:** Decoupled services enable independent scaling,
fault isolation, and deployment autonomy.

### III. Dapr Sidecar Abstraction (NON-NEGOTIABLE)

Application code MUST NOT contain direct dependencies on
infrastructure libraries. Specifically:

- **No direct Kafka client libraries** (e.g., confluent-kafka,
  aiokafka) in application code.
- **No direct database drivers** (e.g., psycopg2, asyncpg) in
  application code for state operations.
- **No direct secret-fetching SDKs** (e.g., azure-keyvault,
  boto3 secrets) in application code.

All infrastructure interaction MUST happen exclusively through
Dapr building blocks:

| Concern | Dapr Building Block | Component Example |
|---------|--------------------|--------------------|
| Messaging | Pub/Sub API | `kafka-pubsub` |
| Persistence | State Management API | `statestore-postgres` |
| Scheduling | Jobs API (alpha1) | `cron-binding` |
| Credentials | Secrets API | `kubernetes-secrets` |

**Enforcement:** Any PR introducing a direct infrastructure
import MUST be rejected during review.

### IV. Dapr Jobs Scheduling

All recurring and deferred task triggers MUST use the Dapr Jobs
API (alpha1). Cron-based polling loops, sleep-based timers, and
OS-level cron jobs are strictly forbidden.

The recurring-engine service MUST register jobs via the Dapr Jobs
API endpoint and react to job callbacks to trigger downstream
events on Kafka.

### V. Dapr State Management

Conversation history and task caching MUST use the Dapr State
Management API with a Postgres-backed state store.

- State keys MUST follow the pattern `{service-name}||{entity-type}||{id}`.
- Concurrency control MUST use ETags for optimistic locking.
- Bulk operations SHOULD be preferred when operating on multiple
  state entries.

### VI. Dapr Secrets for Security

All API keys (Gemini AI), database connection strings, and
third-party credentials MUST be accessed exclusively via the
Dapr Secrets API backed by Kubernetes Secrets.

- **No hardcoded secrets** in source code, environment variables
  baked into images, or config files checked into version control.
- `.env` files are permitted ONLY for local development and MUST
  be listed in `.gitignore`.
- Production secrets MUST reside in Kubernetes Secret objects
  referenced by Dapr secret store components.

### VII. Structured JSON Logging

All services MUST emit logs in structured JSON format to stdout.

Required fields per log entry:

- `timestamp` (ISO 8601)
- `level` (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `service` (service name)
- `trace_id` (propagated from Dapr headers when available)
- `message` (human-readable description)

Plain-text `print()` statements MUST NOT be used for operational
logging. A shared logging configuration module MUST be used across
all three services.

**Rationale:** JSON logs are required for Kubernetes log
aggregation (Fluentd, Loki) and structured querying.

## Tech Stack Constraints

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | Python 3.11+ with FastAPI | All three services |
| Frontend | Next.js | Refactored from `todo-phase-2` reference |
| Frontend-to-Backend | Dapr Service Invocation | No direct REST calls to services |
| Runtime (local) | Kubernetes via Minikube | With Dapr sidecar injector |
| Runtime (production) | AKS or GKE | Managed Kubernetes |
| Messaging | Apache Kafka | Via Strimzi operator or Redpanda Cloud |
| State Store | PostgreSQL | Accessed only via Dapr State API |
| Container Registry | Local registry or ACR/GCR | Per environment |
| Package Manager | pip with `requirements.txt` | One per service |
| Linting | ruff | Enforced in CI |
| Testing | pytest | Unit and integration |

**Forbidden technologies in application code:**
Direct ORM usage (SQLAlchemy, Django ORM), direct Kafka clients,
direct secret managers, direct HTTP calls between services.

## Development Workflow (Agentic Rules)

### Spec-First Mandate

The coding agent is PROHIBITED from writing implementation code
unless a Task ID from `specs/<feature>/tasks.md` is explicitly
referenced. Exploratory prototyping MUST be isolated in branches
prefixed with `spike/` and MUST NOT be merged without a
corresponding spec.

### No Vibe-Coding Policy

Every architectural change MUST be reflected in
`specs/<feature>/plan.md` BEFORE implementation begins. Changes
discovered during implementation that alter the architecture
MUST be back-propagated to the plan before the PR is opened.

### Verification Traceability

Every completed task MUST include a summary referencing which
`spec.md` requirement(s) (FR-XXX identifiers) it satisfies.
Tasks that do not trace to a requirement MUST be justified as
infrastructure or tech-debt items in the PR description.

### Commit Discipline

- Commits MUST reference a Task ID (e.g., `T001`, `T002`).
- One logical change per commit; no mixed concerns.
- Commit messages MUST follow Conventional Commits format:
  `<type>(scope): <description> [TXXX]`

## Governance

This constitution is the authoritative source of truth for all
development decisions in DoneKaro Phase V. It supersedes any
conflicting guidance in READMEs, comments, or ad-hoc discussions.

### Amendment Procedure

1. Propose amendment via a PR modifying this file.
2. Amendment MUST include rationale and impact analysis.
3. All active contributors MUST be notified.
4. Version MUST be bumped per semantic versioning rules below.

### Versioning Policy

- **MAJOR**: Principle removal, redefinition, or backward-incompatible
  governance change.
- **MINOR**: New principle added or existing principle materially
  expanded.
- **PATCH**: Clarification, typo fix, or non-semantic refinement.

### Compliance Review

- Every PR MUST be checked against the 7 core principles.
- The Dapr Sidecar Abstraction principle (III) is NON-NEGOTIABLE
  and MUST trigger automatic rejection on violation.
- Quarterly review of constitution relevance is RECOMMENDED.

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
