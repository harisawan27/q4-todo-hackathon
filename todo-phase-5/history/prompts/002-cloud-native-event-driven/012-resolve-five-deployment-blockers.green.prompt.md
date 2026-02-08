---
id: 012
title: Resolve Five Deployment Blockers
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: developer
command: implement
labels: ["deployment", "blockers", "docker", "frontend", "tests", "secrets"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - secrets.json
  - docker-compose.yaml
  - services/chat-api/Dockerfile
  - services/notification-service/Dockerfile
  - services/recurring-engine/Dockerfile
  - services/chat-api/app/main.py
  - services/notification-service/app/main.py
  - services/recurring-engine/app/main.py
  - services/chat-api/requirements.txt
  - services/notification-service/requirements.txt
  - services/recurring-engine/requirements.txt
  - frontend/lib/api.ts
  - frontend/components/chat-widget.tsx
  - frontend/app/dashboard/layout.tsx
  - frontend/.env.local
  - frontend/package.json
  - frontend/tsconfig.json
  - frontend/tailwind.config.ts
  - frontend/postcss.config.mjs
  - frontend/eslint.config.mjs
  - services/recurring-engine/tests/conftest.py
  - services/recurring-engine/tests/test_recurrence_service.py
  - services/recurring-engine/tests/test_job_service.py
  - services/chat-api/tests/conftest.py
  - services/chat-api/tests/test_health.py
  - services/chat-api/tests/test_state_service.py
  - services/notification-service/tests/conftest.py
  - services/notification-service/tests/test_handlers.py
tests:
  - services/recurring-engine/tests/test_recurrence_service.py (33 passed)
  - services/recurring-engine/tests/test_job_service.py (included in 33)
  - services/chat-api/tests/test_health.py (10 passed)
  - services/chat-api/tests/test_state_service.py (included in 10)
  - services/notification-service/tests/test_handlers.py (5 passed)
  - frontend build (npm run build - success)
---

## Prompt

Implement the following plan:

# Plan: Resolve 5 Deployment Blockers

## Context
All Phase 5 backend code (3 Dapr microservices, K8s manifests, Helm charts) is written but untested and unrunnable. The frontend is missing (only 4 integration files exist), secrets are not configured, Dockerfiles have broken paths, and no tests exist. This plan resolves all 5 blockers to make the system deployable.

Steps: 1) Create secrets.json, 2) Fix Dockerfiles, 3) Fix import paths, 4) Migrate frontend, 5) Add tests.

## Response snapshot

Resolved all 5 deployment blockers:

**Step 1 - secrets.json:** Created with nested keys matching all Dapr secret references (gemini-credentials, auth-credentials, postgres-credentials, vapid-credentials). Values sourced from Phase 2 .env files; VAPID uses placeholder.

**Step 2 - Dockerfiles:** Changed docker-compose.yaml build context to `.` (project root) for all 3 services. Updated all 3 Dockerfiles to use full paths (`services/{name}/requirements.txt`, `services/{name}/app/`) and added `COPY shared/logging/ ./shared/logging/`.

**Step 3 - Import paths:** Added `sys.path.insert(0, os.path.join("..", ".."))` to all 3 main.py files so shared logging is importable from both Docker (`/app/`) and `dapr run -f` (`services/{name}/` CWD).

**Step 4 - Frontend migration:** Bulk-copied Phase 2 frontend (app/, components/, lib/, types/, public/, config files). Preserved Phase 5 files (next.config.ts, Dockerfile, sse-client.ts, task-updates-provider.tsx). Merged api.ts (Phase 2 base + Phase 5 typed wrappers). Fixed chat-widget.tsx (relative URL + JWT auth). Integrated SSE in dashboard layout. Created .env.local. Ran npm install.

**Step 5 - Tests:** Created 8 test files across 3 services. All 48 tests pass (33 recurring-engine, 10 chat-api, 5 notification-service). Frontend builds successfully.

## Outcome

- ✅ Impact: All 5 deployment blockers resolved. System is now testable and buildable.
- 🧪 Tests: 48/48 passing (33 recurring-engine + 10 chat-api + 5 notification-service) + frontend build succeeds
- 📁 Files: 28 files created/modified across backend services, frontend, and infrastructure
- 🔁 Next prompts: Run `docker compose build` to validate full Docker build; deploy to K8s with Helm charts
- 🧠 Reflection: Patching Dapr client mocks requires setting attrs on the imported module object, not replacing the module reference. Phase 2 Capacitor dependencies needed --legacy-peer-deps. Croniter fires at first matching time (same day), not next day.

## Evaluation notes (flywheel)

- Failure modes observed: monkeypatch.setattr replacing module reference doesn't affect already-imported references; croniter same-day firing; npm peer dep conflicts from Capacitor
- Graders run and results (PASS/FAIL): pytest recurring-engine PASS, pytest chat-api PASS, pytest notification-service PASS, npm run build PASS
- Prompt variant (if applicable): n/a
- Next experiment (smallest change to try): Run docker compose build to validate Dockerfile fixes end-to-end
