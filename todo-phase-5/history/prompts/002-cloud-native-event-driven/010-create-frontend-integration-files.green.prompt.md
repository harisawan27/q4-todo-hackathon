---
id: 010
title: Create Frontend Integration Files
stage: green
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: user
command: create files
labels: ["frontend", "sse", "api-client", "docker", "phase-7"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/sse-client.ts
  - frontend/lib/api.ts
  - frontend/components/task-updates-provider.tsx
  - frontend/Dockerfile
  - frontend/next.config.ts
tests:
  - none
---

## Prompt

You are implementing Phase 7 (Frontend Integration) of a Cloud-Native Event-Driven Task System. The project root is `F:\q4-todo-hackathon\todo-phase-5`. Create the following 4 files:

**T073: `frontend/lib/sse-client.ts`** -- React hook `useTaskUpdates(userId)` using `EventSource` connected to `/api/events/stream`. On `task-update` event, invalidate TanStack Query `["tasks"]` cache. Handle auto-reconnect with exponential backoff and error logging.

**T074: `frontend/lib/api.ts`** -- API client using same-origin `/api` prefix. Endpoints should match the chat-api-openapi.yaml contracts: POST /api/chat, GET /api/tasks, GET /api/tasks/{taskId}, PUT /api/tasks/{taskId}, DELETE /api/tasks/{taskId}, POST /api/tasks/{taskId}/complete, GET /api/tasks/{taskId}/audit, POST /api/push/subscribe, POST /api/push/unsubscribe.

**T075: `frontend/components/task-updates-provider.tsx`** -- Component that integrates the `useTaskUpdates` hook into the app layout.

**T076: `frontend/Dockerfile`** -- Multi-stage Node.js 20-alpine build with standalone output.

Also create `frontend/next.config.ts` with `output: "standalone"` and API rewrites.

## Response snapshot

Created all 5 files for Phase 7 Frontend Integration:
- `frontend/lib/sse-client.ts` (T073): React hook with SSE EventSource, TanStack Query cache invalidation, exponential backoff reconnect
- `frontend/lib/api.ts` (T074): Full API client with typed interfaces for Chat, Tasks, Audit, and Push endpoints
- `frontend/components/task-updates-provider.tsx` (T075): Wrapper component providing SSE real-time updates globally
- `frontend/Dockerfile` (T076): Multi-stage build (deps, builder, runner) using node:20-alpine with standalone output
- `frontend/next.config.ts`: Next.js config with standalone output and API proxy rewrites

## Outcome

- Impact: Phase 7 frontend integration scaffolding complete with SSE real-time updates, typed API client, and Docker build
- Tests: none (infrastructure/scaffolding files)
- Files: 5 files created (sse-client.ts, api.ts, task-updates-provider.tsx, Dockerfile, next.config.ts)
- Next prompts: Wire TaskUpdatesProvider into app layout, add TanStack Query provider, create task list UI components
- Reflection: All files created as specified; matches chat-api-openapi.yaml contract endpoints

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A - scaffolding only
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add unit tests for api.ts fetch wrapper and SSE reconnect logic
