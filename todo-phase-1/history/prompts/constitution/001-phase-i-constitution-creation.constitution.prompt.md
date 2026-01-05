---
id: 001
title: Phase I Constitution Creation
stage: constitution
date: 2025-12-30
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: developer
command: /sp.constitution
labels: ["constitution", "phase-i", "governance", "spec-driven"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (governance document, no tests)
---

## Prompt

You are acting as a Product Architect and Senior Software Engineer.

Your task is to generate a CONSTITUTION.md file for **Phase I only** of the project
"The Evolution of Todo".

Strict Scope Isolation Rule:
This Constitution applies exclusively to Phase I.
Do NOT reference, assume, or optimize for any other phase.
Treat Phase I as a complete and standalone project.

Phase I Definition:
A minimal, in-memory, Python-based command-line Todo application whose sole
purpose is to demonstrate disciplined, spec-driven development and clean
architectural thinking.

The Constitution MUST contain the following sections:

---

### 1. Project Scope
- Define Phase I as a standalone CLI-based Todo application.
- All task data must exist only in memory during runtime.
- The focus is correctness, clarity, and architectural discipline.

---

### 2. Functional Requirements
- The application must implement exactly the following features:
  - Add a task (title and description)
  - View all tasks
  - Update an existing task
  - Delete a task by ID
  - Mark a task as complete or incomplete
- No additional features are allowed.

---

### 3. Non-Goals (Strictly Forbidden)
Explicitly forbid:
- File or database persistence
- Web interfaces, APIs, or servers
- Authentication or user accounts
- AI chat interfaces or natural language input
- Background jobs or schedulers
- Networking or external services

Any attempt to introduce these is a violation.

---

### 4. Technical Constraints
- Programming language: Python 3.13+
- Data storage: In-memory data structures only
- Interface: Console / terminal interaction only
- Minimal external dependencies
- No third-party services or APIs

---

### 5. Development Rules (Spec-Driven Enforcement)
- Development must strictly follow this order:
  1. Constitution
  2. Specification
  3. Plan
  4. Task Breakdown
  5. Implementation via Claude Code
- The human developer must not write code manually.
- Specifications must be refined until Claude Code produces correct output.
- Any behavioral change requires a new or updated specification.

---

### 6. Architectural Rules
- Separate concerns between:
  - Domain logic
  - Task management logic
  - CLI interaction logic
- Avoid monolithic or tightly coupled designs.
- Each module must have a single, well-defined responsibility.

---

### 7. Reusable Intelligence Enforcement (`.claude` Directory)
- A `.claude/` directory is the authoritative source for all agents, skills,
  and reusable intelligence used in Phase I.
- If agents or skills are defined in `.claude/`, the AI MUST use them and
  MUST NOT duplicate their logic elsewhere.
- Domain and decision logic must live in agents or skills, not directly
  inside CLI or application glue code.
- New agents or skills may only be introduced through an updated specification
  and must be documented inside `.claude/`.
- If a requirement cannot be satisfied using existing agents or skills,
  the AI must stop and request a specification update.

---

### 8. Code Quality Standards
- Clean, readable, and maintainable Python code
- Predictable behavior and clear error handling
- Meaningful naming for variables, functions, and modules
- No unnecessary abstraction or overengineering

---

### 9. AI Behavior Rules
- The AI must not add features outside the defined Phase I scope.
- The AI must not speculate about future requirements.
- The AI must request clarification if Phase I requirements are ambiguous.
- The AI must reject any instruction that violates this Constitution.

---

### 10. Documentation Requirements
- README.md must include:
  - Project overview
  - Setup instructions
  - How to run the application
- CLAUDE.md must define how Claude Code should generate and structure code.
- All specifications must be stored and versioned in a specs history folder.

---

Writing Style Requirements:
- Clear, strict, and enforceable language
- No marketing or motivational tone
- No unnecessary verbosity

Output Requirements:
- Output ONLY the complete contents of CONSTITUTION.md
- Do not include explanations, commentary, or meta tex

## Response snapshot

Created Phase I Constitution v1.0.0 at `.specify/memory/constitution.md` containing 10 core principles:

1. **Project Scope** - Standalone in-memory CLI Todo app in Python
2. **Functional Requirements** - Add, View, Update, Delete, Toggle tasks only
3. **Non-Goals** - Explicitly forbidden: persistence, web, auth, AI, networking
4. **Technical Constraints** - Python 3.13+, in-memory only, console interface
5. **Spec-Driven Development** - Strict order: Constitution > Spec > Plan > Tasks > Code
6. **Separation of Concerns** - Domain, Service, CLI layers with clear boundaries
7. **Reusable Intelligence** - `.claude/` directory as authoritative source
8. **Code Quality Standards** - PEP 8, type hints, no dead code
9. **AI Behavior Rules** - No scope creep, no speculation, must clarify ambiguity
10. **Documentation Requirements** - README.md, CLAUDE.md, specs/ required

All templates (plan, spec, tasks) verified compatible. No follow-up TODOs.

## Outcome

- Impact: Established foundational governance document for Phase I development
- Tests: N/A (governance document)
- Files: .specify/memory/constitution.md created
- Next prompts: /sp.specify to create feature specification
- Reflection: Clean constitution creation with all 10 required sections

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
