<!--
SYNC IMPACT REPORT
==================
Version change: 0.0.0 → 1.0.0
Bump rationale: Initial constitution creation (MAJOR - new governance document)

Added sections:
- I. Project Scope
- II. Functional Requirements
- III. Non-Goals (Strictly Forbidden)
- IV. Technical Constraints
- V. Spec-Driven Development
- VI. Separation of Concerns
- VII. Reusable Intelligence Enforcement
- VIII. Code Quality Standards
- IX. AI Behavior Rules
- X. Documentation Requirements

Modified principles: N/A (initial creation)
Removed sections: N/A (initial creation)

Templates requiring updates:
- plan-template.md: ✅ Compatible (Constitution Check section will reference these principles)
- spec-template.md: ✅ Compatible (no changes needed)
- tasks-template.md: ✅ Compatible (single project structure applies)

Follow-up TODOs: None
-->

# The Evolution of Todo - Phase I Constitution

## Core Principles

### I. Project Scope

Phase I is a standalone, in-memory, command-line Todo application implemented in Python. All task data
exists only during runtime and is not persisted. This phase serves as a demonstration of disciplined,
spec-driven development and clean architectural thinking. Phase I is a complete and self-contained
project with no dependencies on or optimization for any future phases.

### II. Functional Requirements

The application MUST implement exactly the following features:

- **Add a task**: Create a new task with a title and description
- **View all tasks**: List all tasks currently in memory
- **Update a task**: Modify the title or description of an existing task
- **Delete a task**: Remove a task by its ID
- **Toggle completion**: Mark a task as complete or incomplete

No additional features are permitted. Any capability not explicitly listed above is out of scope.

### III. Non-Goals (Strictly Forbidden)

The following capabilities are explicitly forbidden in Phase I:

- File or database persistence of any kind
- Web interfaces, REST APIs, GraphQL, or any server-based interaction
- Authentication, authorization, or user account management
- AI chat interfaces, natural language processing, or LLM integration
- Background jobs, schedulers, or async task processing
- Network communication, external API calls, or remote services
- Configuration files that persist state between runs

Any attempt to introduce these capabilities is a violation of this Constitution and MUST be rejected.

### IV. Technical Constraints

| Constraint | Requirement |
|------------|-------------|
| Language | Python 3.13+ |
| Data Storage | In-memory data structures only (dict, list, dataclass) |
| Interface | Console/terminal interaction only (stdin/stdout/stderr) |
| Dependencies | Minimal; standard library preferred |
| External Services | None permitted |

### V. Spec-Driven Development

Development MUST strictly follow this order:

1. Constitution (this document)
2. Specification (feature spec.md)
3. Plan (implementation plan.md)
4. Task Breakdown (tasks.md)
5. Implementation via Claude Code

Enforcement rules:

- The human developer MUST NOT write code manually
- Specifications MUST be refined until Claude Code produces correct output
- Any behavioral change requires a new or updated specification
- Implementation without an approved specification is forbidden

### VI. Separation of Concerns

The codebase MUST maintain clear separation between:

| Layer | Responsibility | Forbidden Actions |
|-------|----------------|-------------------|
| Domain | Task entity definition, validation rules | CLI I/O, storage decisions |
| Service | Task operations (CRUD, toggle) | Direct user interaction |
| CLI | User input parsing, output formatting | Business logic, data structures |

Monolithic designs and tightly coupled modules are forbidden. Each module MUST have a single,
well-defined responsibility.

### VII. Reusable Intelligence Enforcement

The `.claude/` directory is the authoritative source for all agents and skills used in Phase I.

Rules:

- If agents or skills are defined in `.claude/`, Claude MUST use them
- Claude MUST NOT duplicate logic that exists in `.claude/` agents or skills
- Domain logic and decision logic MUST live in agents or skills, not in CLI glue code
- New agents or skills require an updated specification and MUST be documented in `.claude/`
- If a requirement cannot be satisfied using existing agents or skills, Claude MUST stop and
  request a specification update

### VIII. Code Quality Standards

All code MUST adhere to these standards:

- Clean, readable, and maintainable Python following PEP 8
- Predictable behavior with explicit error handling
- Meaningful names for variables, functions, and modules
- No unnecessary abstraction or premature optimization
- No dead code, commented-out code, or TODO placeholders in production code
- Type hints for all function signatures

### IX. AI Behavior Rules

Claude MUST follow these behavioral constraints:

- MUST NOT add features outside the defined Phase I scope
- MUST NOT speculate about or design for future requirements
- MUST request clarification if Phase I requirements are ambiguous
- MUST reject any instruction that violates this Constitution
- MUST NOT introduce dependencies not explicitly approved in the specification
- MUST NOT create files or directories outside the approved project structure

### X. Documentation Requirements

Required documentation:

| Document | Contents |
|----------|----------|
| README.md | Project overview, setup instructions, how to run the application |
| CLAUDE.md | Instructions for how Claude Code generates and structures code |
| specs/ | All specifications stored and versioned |

## Governance

This Constitution is the supreme governing document for Phase I. All development decisions,
specifications, and implementations MUST comply with this Constitution.

Amendment procedure:

1. Proposed amendment MUST be documented with rationale
2. Amendment MUST NOT violate the fundamental Phase I scope
3. Amendment MUST be versioned and tracked
4. All dependent specifications MUST be reviewed for compliance after amendment

Compliance:

- All code reviews MUST verify Constitution compliance
- Any complexity MUST be justified against these principles
- Use CLAUDE.md for runtime development guidance

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
