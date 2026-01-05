<!--
  SYNC IMPACT REPORT
  ==================
  Version Change: 1.0.0 → 1.1.0

  Modified Principles: None

  Added Sections:
  - Principle IV: Security Constitution
  - Principle V: Monorepo Navigation
  - Principle VI: Iteration Goal

  Removed Sections: None

  Templates Validation:
  - .specify/templates/plan-template.md ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md ✅ Compatible (requirements align)
  - .specify/templates/tasks-template.md ✅ Compatible (phase structure aligns)

  Deferred TODOs:
  - ⚠ frontend/CLAUDE.md - To be created when frontend directory is initialized
  - ⚠ backend/CLAUDE.md - To be created when backend directory is initialized
-->

# Agentic AI Todo Hackathon - Phase II Constitution

## Core Principles

### I. Agentic Workflow Supremacy

You are the Lead Architect for Phase II of the Agentic AI Todo Hackathon. All development MUST follow the agentic workflow:

- **Spec-First Development**: DO NOT write code manually without a spec reference. Code without a spec is unauthorized.
- **Mandatory Loop**: ALWAYS follow: Read `@specs` → Generate Plan (`/sp.plan`) → Break into Tasks (`/sp.tasks`) → Implement (`/sp.implement`).
- **Spec-Kit Plus Integration**: If a spec is missing, inform the user and WAIT for the spec to be created via Spec-Kit Plus commands. Never proceed without specification.
- **No Ad-Hoc Implementation**: Every feature, fix, or enhancement MUST trace back to a documented specification.

**Rationale**: Agentic workflows ensure traceability, reproducibility, and alignment between intent and implementation. Manual coding bypasses validation gates and introduces untracked technical debt.

### II. Core Stack Integrity

The technology stack is fixed and MUST NOT be deviated from without constitutional amendment:

| Layer | Technology | Version Requirement |
|-------|------------|---------------------|
| Frontend | Next.js (App Router) | 16+ |
| Frontend Language | TypeScript | Strict mode |
| Styling | Tailwind CSS | Latest |
| Backend | FastAPI | Latest |
| Backend ORM | SQLModel | Latest |
| Backend Language | Python | 3.13+ |
| Database | Neon Serverless PostgreSQL | N/A |
| Auth (Frontend) | Better Auth | Latest |
| Auth (Backend) | JWT Verification (python-jose) | Latest |

**Enforcement Rules**:
- Adding new frameworks, libraries, or languages requires ADR approval.
- Downgrading versions is prohibited without migration plan.
- All dependencies MUST be pinned to specific versions in lock files.
- Environment-specific configuration MUST use `.env` files (never hardcode secrets).

**Rationale**: Stack consistency prevents integration issues, reduces cognitive load, and ensures all team members operate with shared assumptions.

### III. Reusable Intelligence & Agents

Custom skills and agents are authoritative sources for domain-specific logic:

- **Mandatory Consultation**: ALWAYS consult `.claude/skills/` and `.claude/agents/` before modifying Auth, API routes, or domain operations.
- **Auth Architect Agent**: Use the `auth-architect` agent (`.claude/agents/auth-architect/AGENT.md`) for ANY security-related task. No route may be created without JWT protection.
- **Better Auth Config Skill**: Apply the `better-auth-config` skill (`.claude/skills/better-auth-config/SKILL.md`) whenever bridge logic between TypeScript and Python is required.
- **Domain Operation Skills**: For todo operations, invoke the corresponding skill from `.claude/skills/`:
  - `create-task`, `update-task`, `delete-task`, `list-tasks`
  - `toggle-task`, `reschedule-task`, `set-priority`, `manage-tags`
- **Agent Pipeline**: Follow the agent pipeline for all operations:
  - IntentResolution → SpecGovernance → TodoDomain → ExecutionPlanner → InfrastructureAdapter

**Enforcement Rules**:
- Skills define input/output contracts—follow them exactly.
- Agent forbidden decisions MUST be respected.
- AuthArchitect red lines (unprotected routes, missing user filters, hardcoded secrets) MUST block implementation.

**Rationale**: Reusable intelligence encapsulates domain expertise and security requirements. Bypassing agents leads to inconsistent behavior and security vulnerabilities.

### IV. Security Constitution

Every API endpoint MUST be protected by cryptographic verification to ensure 100% user data isolation:

- **JWT Verification Dependency**: Every FastAPI endpoint MUST include `Depends(get_current_user)` which verifies the JWT signature using `BETTER_AUTH_SECRET`.
- **User ID Trust Boundary**: NEVER trust a `user_id` from URL parameters, query strings, or request bodies. The ONLY trusted source is the `sub` claim extracted from the verified JWT.
- **Shared Secret Synchronization**: Both frontend (Better Auth) and backend (python-jose) MUST use the identical `BETTER_AUTH_SECRET` environment variable. Mismatched secrets = authentication failure.
- **Query-Level Isolation**: All database queries MUST include `.where(...user_id == current_user.user_id)` to enforce tenant isolation at the data layer.

**Security Red Lines** (implementation MUST be blocked if violated):
| Violation | Impact | Action |
|-----------|--------|--------|
| Route without `Depends(get_current_user)` | Unauthenticated access | BLOCK |
| Query without `user_id` filter | Cross-tenant data leak | BLOCK |
| Trusting `user_id` from URL/body | Privilege escalation | BLOCK |
| Hardcoded `BETTER_AUTH_SECRET` | Credential exposure | BLOCK |
| Mismatched secrets between services | Auth bypass | BLOCK |

**Rationale**: Cryptographically signed tokens are the single source of truth for user identity. Any deviation enables unauthorized data access or privilege escalation.

### V. Monorepo Navigation

Context-aware development requires adherence to layer-specific guidance files:

- **Frontend Context**: When editing files in the `frontend/` directory, follow `frontend/CLAUDE.md` for frontend-specific conventions, component patterns, and styling rules.
- **Backend Context**: When editing files in the `backend/` directory, follow `backend/CLAUDE.md` for API design, database patterns, and security implementation.
- **Root Index**: The root `CLAUDE.md` serves as the primary index and MUST reference all specifications, skills, agents, and layer-specific guidance files.
- **Context Switching**: When transitioning between frontend and backend work, explicitly acknowledge the context switch and load the appropriate guidance file.

**Directory Structure**:
```
/
├── CLAUDE.md              # Primary index (this file references all others)
├── frontend/
│   ├── CLAUDE.md          # Frontend-specific guidance
│   └── ...
├── backend/
│   ├── CLAUDE.md          # Backend-specific guidance
│   └── ...
├── .claude/
│   ├── skills/            # Domain operation skills
│   └── agents/            # Specialized agent personas
└── .specify/
    └── memory/
        └── constitution.md # This file
```

**Rationale**: Monorepo development requires clear boundaries between layers. Context-specific guidance prevents cross-contamination of concerns and ensures consistent patterns within each layer.

### VI. Iteration Goal

The Phase II mission is a complete transformation of the Phase I CLI application:

**Source State (Phase I)**:
- CLI-only todo application
- Single-user, local storage
- No authentication
- No persistence beyond local files

**Target State (Phase II)**:
- Modern multi-user web application
- Next.js 16+ frontend with Better Auth
- FastAPI backend with SQLModel
- Neon PostgreSQL for persistent storage
- 100% user data isolation via JWT-based authentication
- Cryptographically signed tokens for all API access

**Success Criteria**:
- [ ] All Phase I CLI features accessible via web UI
- [ ] User registration and authentication functional
- [ ] Each user sees ONLY their own tasks (data isolation verified)
- [ ] JWT tokens issued by Better Auth, verified by FastAPI
- [ ] No cross-user data leakage under any circumstances
- [ ] Persistent storage survives server restarts

**Non-Goals** (out of scope for Phase II):
- Real-time collaboration features
- Offline-first/PWA capabilities
- Third-party OAuth providers
- Admin dashboard or multi-tenancy management

**Rationale**: Clear transformation goals prevent scope creep and ensure focused delivery. The Phase I → Phase II migration is complete when all success criteria are met.

## Technology Stack Requirements

### Frontend Requirements

- Use Next.js 16+ App Router (no Pages Router).
- TypeScript strict mode enabled (`"strict": true` in tsconfig).
- Tailwind CSS for all styling (no custom CSS unless absolutely necessary).
- Better Auth for authentication with JWT plugin.
- All API calls MUST include `Authorization: Bearer <token>` header.

### Backend Requirements

- FastAPI for all API endpoints.
- SQLModel for database models and queries.
- Python 3.13+ with type hints on all functions.
- All routes MUST include `Depends(get_current_user)` dependency.
- All SQLModel queries MUST filter by `user_id` from JWT `sub` claim.
- Use python-jose for JWT verification with `BETTER_AUTH_SECRET`.

### Database Requirements

- Neon Serverless PostgreSQL as the single source of truth.
- All schema changes via migrations (never modify production directly).
- User data isolation enforced at query level (multi-tenant by user_id).

### Security Requirements (Non-Negotiable)

- [ ] Every protected route has `Depends(get_current_user)`
- [ ] Every query includes `.where(...user_id == current_user.user_id)`
- [ ] No hardcoded secrets (use `BETTER_AUTH_SECRET` env var)
- [ ] No tokens in URL parameters (use headers only)
- [ ] Error responses do not leak sensitive information

## Development Workflow

### Spec-Driven Development Loop

```
1. /sp.specify   → Create feature specification
2. /sp.clarify   → Resolve ambiguities (if needed)
3. /sp.plan      → Generate implementation plan
4. /sp.tasks     → Break into actionable tasks
5. /sp.implement → Execute tasks sequentially
6. /sp.phr       → Record prompt history (automatic)
7. /sp.adr       → Document architectural decisions (when significant)
```

### Pre-Implementation Checklist

Before writing any code:
- [ ] Spec exists at `specs/<feature>/spec.md`
- [ ] Plan exists at `specs/<feature>/plan.md`
- [ ] Tasks exist at `specs/<feature>/tasks.md`
- [ ] Relevant skills/agents consulted
- [ ] AuthArchitect security checklist reviewed

### Code Review Requirements

All PRs MUST verify:
- Traceability to spec/task
- Compliance with stack integrity
- Security checklist passed
- Skills/agents consulted where applicable

## Governance

### Constitutional Authority

This Constitution supersedes all other practices, conventions, or preferences. In case of conflict:
1. Constitution takes precedence
2. ADRs (Architecture Decision Records) clarify specific decisions
3. Skills/Agents provide domain-specific guidance
4. General best practices apply only where not contradicted above

### Amendment Procedure

1. **Proposal**: Document proposed change with rationale
2. **ADR**: Create ADR documenting decision context and alternatives
3. **Review**: User approval required
4. **Migration**: If breaking change, provide migration plan
5. **Version Bump**:
   - MAJOR: Backward incompatible changes (principle removal/redefinition)
   - MINOR: New principles/sections added
   - PATCH: Clarifications, typo fixes

### Compliance Verification

- All PRs must pass Constitution Check (see plan-template.md)
- Violations must be justified in Complexity Tracking table
- Unjustified violations block merge

### Guidance Files

- Runtime development guidance: `CLAUDE.md`
- Frontend guidance: `frontend/CLAUDE.md`
- Backend guidance: `backend/CLAUDE.md`
- Skills directory: `.claude/skills/`
- Agents directory: `.claude/agents/`
- Spec-Kit Plus templates: `.specify/templates/`

**Version**: 1.1.0 | **Ratified**: 2026-01-05 | **Last Amended**: 2026-01-05
