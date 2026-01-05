---
id: 002
title: Constitution Amended Security Navigation Goal
stage: constitution
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: architect
command: /sp.constitution
labels: ["constitution", "amendment", "security", "monorepo", "iteration-goal"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (governance document)
---

## Prompt

```text
/sp.constitution "### 4. SECURITY CONSTITUTION
- Every API endpoint MUST be protected by a JWT verification dependency in FastAPI.
- No 'user_id' from a URL parameter should be trusted unless it matches the 'sub' claim in the verified JWT.
- Shared Secret: Both services must use 'BETTER_AUTH_SECRET'.

### 5. MONOREPO NAVIGATION
- Context Awareness: When editing the frontend, follow @frontend/CLAUDE.md. When editing the backend, follow @backend/CLAUDE.md.
- Maintain the root CLAUDE.md as the primary index for all specifications.

### 6. ITERATION GOAL
Transform the Phase I CLI app into a modern, multi-user web application with persistent storage, ensuring 100% user data isolation via cryptographically signed tokens."
```

## Response snapshot

Amended Phase II Constitution from v1.0.0 to v1.1.0 with three new principles:

**IV. Security Constitution**:
- JWT verification dependency (`Depends(get_current_user)`) mandatory on all endpoints
- User ID trust boundary: ONLY trust `sub` claim from verified JWT, never URL params
- Shared secret synchronization: `BETTER_AUTH_SECRET` must match between frontend/backend
- Query-level isolation: All queries must filter by `user_id`
- Security red lines table with BLOCK actions for violations

**V. Monorepo Navigation**:
- Context-aware development: `frontend/CLAUDE.md` for frontend, `backend/CLAUDE.md` for backend
- Root `CLAUDE.md` as primary index
- Directory structure documented
- Context switching acknowledgment required

**VI. Iteration Goal**:
- Source state: Phase I CLI (single-user, local, no auth)
- Target state: Phase II Web (multi-user, Neon PostgreSQL, JWT auth)
- Success criteria checklist (6 items)
- Non-goals explicitly defined (no real-time, no PWA, no OAuth, no admin)

## Outcome

- ✅ Impact: Constitution expanded from 3 to 6 principles, security hardening codified
- 🧪 Tests: N/A (governance document)
- 📁 Files: 1 modified (.specify/memory/constitution.md)
- 🔁 Next prompts: Create frontend/CLAUDE.md and backend/CLAUDE.md when directories initialized
- 🧠 Reflection: Security constitution elevates JWT verification from guidance to constitutional requirement; iteration goal provides clear Phase I→II transformation criteria

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (governance document)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Validate security red lines during first API route implementation
