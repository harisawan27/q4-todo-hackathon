---
id: 006
title: Plan Update Sequences CICD Migration
stage: plan
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: lenovo
command: /sp.plan
labels: ["plan-update", "sequence-diagrams", "cicd", "dockerfile", "helm", "migration", "dapr-service-invocation"]
links:
  spec: specs/002-cloud-native-event-driven/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-cloud-native-event-driven/plan.md
tests:
  - n/a (planning phase)
---

## Prompt

you missed remaining part of the prevoius prompt, so also include that and update plan 'Map the sequence flow:

User Action → Chat API → Dapr Publish → Kafka → Worker Services → Dapr State/Notification.

4. Infrastructure & Deployment Strategy
Containerization: Define Dockerfile requirements for each service (multi-stage builds for optimization).

Kubernetes Orchestration: Plan the Helm charts or K8s manifests for deployment.

CI/CD: Outline a GitHub Actions workflow to build images and deploy to Azure (AKS)/Google (GKE).

5. Migration Strategy from Phase 2
Detail how to extract the core logic from the Phase 2 backend and 'wrap' it in the new Dapr-enabled microservices.

Specify how the frontend will be updated to communicate with the services via the Dapr Sidecar (Service Invocation).
'

## Response snapshot

Updated plan.md with three major sections that were missing from the original plan:

**Section 4.5 — End-to-End Sequence Flows (expanded from 3 to 5 sequences)**:
- Master flow diagram showing full system topology: Browser → Frontend → Ingress → chat-api → Dapr → Kafka → Workers → State/Notification
- Sequence 1: Task creation with full ASCII sequence diagram showing all actors including Ingress and Dapr sidecar
- Sequence 2: Recurring task completion → auto-generate next instance (15-step flow with Dapr transactions)
- Sequence 3: Due-date reminder → push notification (3-phase: registration, firing, delivery with failure handling)
- Sequence 4: Real-time cross-client SSE update flow
- Sequence 5: Graceful degradation when notification-service is down (FR-009)

**Section 7 — Infrastructure & Deployment Strategy (expanded from bullet points to full specs)**:
- Multi-stage Dockerfiles for Python services (builder + runtime, non-root, ~150MB images) and Next.js frontend (deps + builder + standalone, ~80MB)
- Complete Helm chart structure with values.yaml, values-production.yaml, deployment templates with Dapr annotations
- Full GitHub Actions CI/CD workflow: lint-test (parallel matrix) → frontend-build → build-images (push to ACR/GCR) → integration-test (Dapr) → deploy-production (Helm upgrade with manual approval gate) → smoke test
- GKE variant deployment job
- CI/CD pipeline flow diagram

**Section 8 — Migration Strategy (expanded from mapping table to full extraction guide)**:
- Strangler Fig pattern: extract module-by-module, wrap in Dapr services
- Concrete code examples showing Phase 2 → Phase 5 wrapping (e.g., tools.py add_task with direct DB → Dapr State + Pub/Sub)
- Step-by-step extraction for each service (chatbot core, notification logic, recurring engine)
- Frontend Dapr Service Invocation architecture: browser → Ingress → chat-api (client-side), Next.js API routes → Dapr sidecar → chat-api (server-side)
- Frontend api.ts diff showing exact changes needed
- New SSE client integration with TanStack Query invalidation
- Complete migration mapping table (30+ components)
- What gets dropped table (12 components with reasons)
- Recommended migration order (6 phases, ~5 weeks)

## Outcome

- Impact: Plan.md now covers all technical details originally requested — sequences, Dockerfiles, Helm, CI/CD, migration extraction, and frontend Dapr invocation
- Tests: No tests (planning phase)
- Files: 1 file updated (plan.md — added ~500 lines across 3 major sections)
- Next prompts: `/sp.tasks` to generate implementation task list from the now-complete plan
- Reflection: The original plan covered architecture and contracts well but lacked operational specifics (Dockerfiles, CI/CD) and concrete migration guidance (code-level wrapping examples). This update fills those gaps with production-ready specifications.

## Evaluation notes (flywheel)

- Failure modes observed: None — incremental update to existing file
- Graders run and results (PASS/FAIL): Constitution alignment PASS (all 7 principles maintained in expanded sections)
- Prompt variant (if applicable): Follow-up /sp.plan with specific missing sections identified by user
- Next experiment (smallest change to try): Validate multi-stage Dockerfile builds locally before implementation
