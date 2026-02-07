---
id: 001
title: Init DoneKaro Phase V Constitution
stage: constitution
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: none
branch: 001-cloud-native-chatbot
user: architect
command: /sp.constitution
labels: ["constitution", "initialization", "governance", "dapr", "cloud-native"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

I need to initialize my speckit.constitution for Phase V of the DoneKaro project. This file must serve as the technical 'Source of Truth' that governs all your agentic coding decisions. Use the following principles and constraints to generate a structured constitution:

1. Core Architecture Pattern
Cloud-Native Microservices: The application must be decomposed into three primary services: chat-api, notification-service, and recurring-engine.

Event-Driven Architecture (EDA): Services must never communicate directly (synchronously). All inter-service logic must be triggered by events published to Kafka.

Dapr Sidecar Pattern: Direct infrastructure dependencies (Kafka, Postgres, Secrets) are strictly forbidden in the application code. All infrastructure interaction MUST happen via Dapr building blocks (Pub/Sub, State Management, Jobs API, and Secrets).

2. Tech Stack Constraints
Backend: Python (FastAPI) for all services.

Frontend: Next.js (Phase 2 reference 'todo-phase-2') refactored for Service Invocation via Dapr.

Runtime: Kubernetes (Minikube for local, AKS/GKE for production).

Messaging: Kafka (using Strimzi operator or Redpanda Cloud).

3. Development Workflow (Agentic Rules)
Spec-First: You are prohibited from writing code unless a Task ID from speckit.tasks is referenced.

No 'Vibe-Coding': Every architectural change must be reflected in speckit.plan before implementation.

Verification: Every implemented task must include a summary of which speckit.specify requirement it satisfies.

4. Specific Implementation Standards
Reminders: Use the Dapr Jobs API (alpha1) for scheduling triggers, not cron polling.

State: Use Dapr State Management for conversation history and task caching.

Security: All API keys (Gemini, DB strings) must be accessed via the Dapr Secrets API from K8s secrets.

Logging: Standardize JSON logging across all services for Kubernetes observability.

Please generate the final speckit.constitution file based on these instructions."

## Response snapshot

Generated DoneKaro Phase V constitution v1.0.0 with 7 core principles:

1. **Cloud-Native Microservices** — Three services: chat-api, notification-service, recurring-engine
2. **Event-Driven Architecture** — Kafka-only inter-service communication, no synchronous coupling
3. **Dapr Sidecar Abstraction (NON-NEGOTIABLE)** — All infra via Dapr building blocks (Pub/Sub, State, Jobs, Secrets)
4. **Dapr Jobs Scheduling** — Jobs API (alpha1) for recurring triggers, no cron polling
5. **Dapr State Management** — Postgres-backed state store with ETag concurrency
6. **Dapr Secrets for Security** — K8s Secrets via Dapr Secrets API, no hardcoded credentials
7. **Structured JSON Logging** — Standardized JSON log format across all services

Plus sections for Tech Stack Constraints (Python/FastAPI, Next.js, K8s, Kafka), Development Workflow (spec-first, no vibe-coding, verification traceability), and Governance (amendment procedure, semantic versioning, compliance review).

All templates validated for consistency — no updates required.

## Outcome

- ✅ Impact: Constitution established as authoritative source of truth for DoneKaro Phase V
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (created)
- 🔁 Next prompts: /sp.specify to create feature spec, /sp.plan for architecture planning
- 🧠 Reflection: User provided comprehensive input covering all 4 principle areas; template extended from 6 to 7 principle slots to accommodate all distinct rules

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS — no unresolved placeholders, dates ISO format, all principles declarative and testable
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
