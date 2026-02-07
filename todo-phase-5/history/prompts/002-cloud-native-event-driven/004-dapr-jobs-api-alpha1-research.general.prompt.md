---
id: 004
title: Dapr Jobs API Alpha1 Research
stage: general
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: user
command: research
labels: ["dapr", "jobs-api", "alpha1", "scheduling", "cron", "callbacks", "recurring-engine", "fastapi"]
links:
  spec: specs/002-cloud-native-event-driven/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/002-cloud-native-event-driven/004-dapr-jobs-api-alpha1-research.general.prompt.md
tests:
  - none (research deliverable)
---

## Prompt

Research the Dapr Jobs API (alpha1) for scheduling. I need to know:
1. Current API surface (endpoints, request/response schemas)
2. How to register, trigger, and cancel jobs
3. Cron schedule format supported
4. How callbacks work (does Dapr call back to the app? What endpoint?)
5. Limitations and known issues of the alpha1 API
6. Configuration in Dapr components YAML
7. Any examples of using Jobs API with Python/FastAPI

Search the official Dapr docs and GitHub. Report everything you find with concrete API examples.

## Response snapshot

Delivered comprehensive research report covering all 7 areas with concrete curl, YAML, and Python/FastAPI code examples:
1. Full API surface: 3 HTTP endpoints (POST/GET/DELETE) at /v1.0-alpha1/jobs/<name> with request/response schemas for schedule, dueTime, repeats, ttl, and data fields
2. Registration via POST (upsert semantics), cancellation via DELETE, no manual trigger (Dapr auto-triggers based on schedule/dueTime)
3. Three schedule formats: 6-field cron (with seconds), systemd @every intervals, and predefined (@hourly, @daily, etc.); 5-field cron auto-prefixed with 0 seconds
4. Callback mechanism: Dapr sends PUT /job/<job-name> to app on app-port with data payload; app must return 200; all replicas receive callback (broadcast)
5. Ten known limitations: no retry on missed callbacks, broadcast to all replicas, no job history, no bulk operations, no pause/resume, single app-id scope, alpha API instability
6. No component YAML needed (scheduler is a control plane service); configured via Helm values.yaml and Kubernetes deployment annotations (dapr.io/app-port is critical)
7. Complete FastAPI implementation: DaprJobsClient class, lifespan job registration, PUT /job/{job_name} callback handler, one-shot reminders, recurring schedules, pytest examples

Key architecture recommendations for DoneKaro: recurring-engine owns all jobs, single replica or idempotent handlers, startup reconciliation for missed callbacks, action-based routing in data payload, DaprJobsClient abstraction for API stability.

## Outcome

- Impact: Research deliverable providing complete implementation reference for Dapr Jobs API in recurring-engine service, directly supporting constitution Principle IV (Dapr Jobs Scheduling)
- Tests: none (research deliverable)
- Files: 1 file created (this PHR)
- Next prompts: /sp.plan to incorporate Jobs API patterns into architectural plan, or /sp.adr for single-replica vs idempotent-handler decision
- Reflection: WebSearch, WebFetch, and curl-based Bash commands were all denied (network access restricted in this environment). Report drawn from training knowledge of Dapr 1.14 documentation. All patterns align with constitution Principle III (Dapr sidecar abstraction) and Principle IV (Dapr Jobs scheduling). Recommend verifying callback HTTP method (PUT vs POST) and scheduler configuration against live docs.

## Evaluation notes (flywheel)

- Failure modes observed: WebSearch, WebFetch, and network-accessing Bash commands all auto-denied; fell back to training knowledge. Intermittent Bash permission denials for non-network commands (resolved on retry).
- Graders run and results (PASS/FAIL): Manual review required -- verify against docs.dapr.io for any API changes post May 2025
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Verify callback HTTP method (PUT vs POST) and whether Dapr 1.15+ changed the alpha1 API path or added retry/leader-election features
