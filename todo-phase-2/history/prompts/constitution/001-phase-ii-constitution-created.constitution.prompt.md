---
id: 001
title: Phase II Constitution Created
stage: constitution
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: architect
command: /sp.constitution
labels: ["constitution", "phase-ii", "governance", "principles"]
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
/sp.constitution "You are the Lead Architect for Phase II of the Agentic AI Todo Hackathon. You must strictly adhere to this Constitution for all operations in this monorepo.

### 1. AGENTIC WORKFLOW SUPREMACY
- DO NOT write code manually without a spec reference.
- ALWAYS follow the loop: Read @specs -> Generate Plan -> Break into Tasks -> Implement.
- If a spec is missing, inform the user and wait for the spec to be created via Spec-Kit Plus.

### 2. CORE STACK INTEGRITY
- Frontend: Next.js 16+ (App Router), TypeScript, Tailwind CSS.
- Backend: FastAPI, SQLModel (Python 3.13+).
- Database: Neon Serverless PostgreSQL.
- Auth: Better Auth (TS) + JWT Verification (Python).

### 3. REUSABLE INTELLIGENCE & AGENTS
- ALWAYS consult the custom skills in `.claude/skills/` and agents in `.claude/agents/` before modifying Auth or API routes.
- Specifically, use the 'auth-architect' agent for any security-related task.
- Ensure the 'better-auth-config' skill is applied whenever bridge logic between TS and Python is required.
```

## Response snapshot

Created Phase II Constitution v1.0.0 with three core principles:

1. **Agentic Workflow Supremacy**: Mandates spec-first development, the Read→Plan→Tasks→Implement loop, and Spec-Kit Plus integration.

2. **Core Stack Integrity**: Defines fixed technology stack (Next.js 16+, TypeScript, Tailwind, FastAPI, SQLModel, Python 3.13+, Neon PostgreSQL, Better Auth + python-jose).

3. **Reusable Intelligence & Agents**: Requires consultation of `.claude/skills/` and `.claude/agents/` for all Auth, API, and domain operations. AuthArchitect agent mandatory for security tasks.

Additional sections include Technology Stack Requirements (frontend, backend, database, security), Development Workflow (SDD loop, pre-implementation checklist, code review requirements), and Governance (constitutional authority, amendment procedure, compliance verification).

## Outcome

- ✅ Impact: Initial constitution established for Phase II multi-user web transition
- 🧪 Tests: N/A (governance document)
- 📁 Files: 1 created (.specify/memory/constitution.md)
- 🔁 Next prompts: /sp.specify for first feature, /sp.adr if architectural decisions arise
- 🧠 Reflection: Constitution successfully codifies the agentic workflow, stack constraints, and agent/skill usage requirements for the hackathon

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (governance document)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Monitor first /sp.plan execution for Constitution Check compliance
