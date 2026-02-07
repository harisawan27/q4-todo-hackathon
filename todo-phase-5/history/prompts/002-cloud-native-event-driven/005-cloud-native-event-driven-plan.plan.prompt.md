---
id: 005
title: Cloud-Native Event-Driven Architecture Plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: lenovo
command: /sp.plan
labels: ["dapr", "microservices", "event-driven", "kafka", "kubernetes", "architecture"]
links:
  spec: specs/002-cloud-native-event-driven/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-cloud-native-event-driven/plan.md
  - specs/002-cloud-native-event-driven/research.md
  - specs/002-cloud-native-event-driven/data-model.md
  - specs/002-cloud-native-event-driven/quickstart.md
  - specs/002-cloud-native-event-driven/contracts/chat-api-openapi.yaml
  - specs/002-cloud-native-event-driven/contracts/event-schemas.yaml
  - specs/002-cloud-native-event-driven/contracts/dapr-subscriptions.yaml
tests:
  - n/a (planning phase - no implementation tests)
---

## Prompt

This plan must act as the technical blueprint for refactoring our Phase 2 full-stack app into a Dapr-enabled, event-driven microservices architecture.

Please structure the plan with the following technical details:

1. Service Decomposition & Folder Structure
Define the boundaries for three microservices: chat-api (FastAPI), notification-service (Python Worker), and recurring-engine (Python Worker).

Map out a directory structure that separates /services, /dapr-components, /k8s-manifests, and the /frontend.

2. Dapr Component Architecture
State Store: Plan a state.postgresql component (using Neon DB) for conversation history and task state.

Pub/Sub: Plan a pubsub.kafka component using Strimzi (local) or Redpanda (cloud).

Secret Store: Plan a secretstores.kubernetes component to handle Gemini and Database credentials.

Cron/Jobs: Plan the Dapr Jobs API (alpha1) setup for reminder scheduling.

3. Event Schema & Communication Flow
Design the JSON schema for Kafka topics: task-events, reminders, and task-updates.

Map the seq

## Response snapshot

Generated comprehensive implementation plan with 7 artifacts covering the full technical blueprint for Phase 2 → Phase 5 migration:

**plan.md**: Complete implementation plan with 8 sections covering service decomposition (3 services with clear ownership boundaries), directory structure, Dapr component architecture (state.postgresql.v2, pubsub.kafka, secretstores.kubernetes, Jobs API alpha1), event schema design (CloudEvents 1.0 with 5 event types across 3 Kafka topics), frontend integration strategy (SSE bridge), shared infrastructure (JSON logging, Dapr HTTP client pattern), deployment strategy (Minikube/AKS/GKE), and Phase 2 migration mapping.

**research.md**: 6 research items resolved — PostgreSQL v2 (index-key pattern for lacking Query API), Dapr Pub/Sub Kafka (Strimzi local/Redpanda Cloud prod), Jobs API alpha1 (with cron binding fallback), broker selection, SSE vs WebSocket, and secrets management.

**data-model.md**: 8 entities defined with Pydantic schemas, Dapr state key patterns, index-key strategies, and Phase 2 migration mapping.

**contracts/**: OpenAPI 3.1 spec for chat-api (11 endpoints), CloudEvents event schemas for all 3 Kafka topics (7 event types), and declarative Dapr subscription CRDs.

**quickstart.md**: 3 local dev options (Minikube, Docker Compose, Dapr multi-app run) with step-by-step setup instructions.

Constitution Check: ALL 7 principles PASS. Two ADR suggestions surfaced.

## Outcome

- Impact: Full architectural blueprint generated covering service boundaries, Dapr components, event schemas, data models, API contracts, and deployment strategy
- Tests: No tests (planning phase)
- Files: 7 files created (plan.md, research.md, data-model.md, quickstart.md, 3 contract files)
- Next prompts: `/sp.tasks` to generate implementation task list, `/sp.adr dapr-postgresql-state-store-version-selection`, `/sp.adr kafka-broker-selection`
- Reflection: Comprehensive plan covers all user-requested technical details. Research identified critical v2 state store limitation (no Query API) requiring index-key pattern workaround. Dapr Jobs API alpha1 risk acknowledged with cron binding fallback.

## Evaluation notes (flywheel)

- Failure modes observed: Agent context update script failed (template not at repo root); spec.md path mismatch between setup script (repo root) and actual location (todo-phase-5/)
- Graders run and results (PASS/FAIL): Constitution Check PASS (7/7 principles), Spec Alignment PASS (FR-001 through FR-018 addressed)
- Prompt variant (if applicable): sp.plan with user-provided technical structure requirements
- Next experiment (smallest change to try): Validate Dapr Jobs API alpha1 availability in target Dapr runtime version before implementation
