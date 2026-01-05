---
id: 002
title: Update Spec With Technical Constraints
stage: spec
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: 001-multi-user-web
branch: 001-multi-user-web
user: system
command: /sp.specify
labels: ["specification", "update", "technical-constraints", "api-contract", "mobile-responsive"]
links:
  spec: specs/001-multi-user-web/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-multi-user-web/spec.md
  - specs/001-multi-user-web/checklists/requirements.md
tests:
  - N/A (specification phase - no tests)
---

## Prompt

previus prompt was incomplete, the is it's remaining prompt so update specification according to these remaining prompt, "3. **Database:** Design a SQLModel schema for 'Users' and 'Tasks' with a foreign key relationship (user_id).
4. **Data Isolation:** All database queries MUST filter by the authenticated user's ID.
5. **Frontend:** Build a modern Next.js 16 dashboard with Tailwind CSS.

### Technical Constraints
- **Monorepo Structure:** Keep frontend and backend in separate folders but within this repo.
- **Security:** Use 'BETTER_AUTH_SECRET' for both JWT issuance (TS) and verification (Python).
- **Tooling:** Refer to @.claude/skills/better-auth-config and invoke the @.claude/agents/auth-architect persona for all security implementation.
- **Endpoints:** Match the REST specification: GET/POST /api/tasks, and GET/PUT/DELETE/PATCH /api/tasks/{id}.

### Acceptance Criteria
- User can log in and stay logged in via JWT.
- API returns 401 Unauthorized if no valid token is provided.
- Frontend displays only the current user's tasks.
- Mobile-responsive UI using Tailwind.""

## Response snapshot

Updated the existing specification to incorporate the remaining requirements:

**New Additions**:
1. **User Story 7**: Mobile-Responsive Dashboard (P2 priority)
2. **Acceptance Scenarios 1.5, 1.6**: Persistent JWT login and 401 unauthorized access
3. **FR-015**: 401 Unauthorized response requirement
4. **FR-016**: Responsive interface requirement
5. **SC-009**: Viewport responsiveness criterion (320px - 1920px)
6. **Technical Constraints Section**: Documenting monorepo structure, shared secret, API contract patterns

**Files Updated**:
- `specs/001-multi-user-web/spec.md` - Added new user story, requirements, and technical constraints
- `specs/001-multi-user-web/checklists/requirements.md` - Updated with change log

## Outcome

- Impact: Spec now fully captures all user requirements including technical constraints and mobile responsiveness
- Tests: N/A (specification phase)
- Files: 2 files updated (spec.md, requirements checklist)
- Next prompts: `/sp.clarify` for additional clarification or `/sp.plan` to begin architectural planning
- Reflection: Technical Constraints section appropriately separates implementation guidance from user-facing requirements

## Evaluation notes (flywheel)

- Failure modes observed: None - update completed successfully
- Graders run and results (PASS/FAIL): Content Quality PASS, Requirement Completeness PASS, Feature Readiness PASS
- Prompt variant (if applicable): Spec update workflow (not new feature)
- Next experiment (smallest change to try): N/A - spec is complete and ready for planning
