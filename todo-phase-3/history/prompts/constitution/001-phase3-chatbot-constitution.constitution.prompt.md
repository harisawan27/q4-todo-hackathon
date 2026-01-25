---
id: 001
title: Phase 3 Chatbot Constitution Creation
stage: constitution
date: 2026-01-25
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-multi-user-web
user: Muhammad Haris Awan
command: /sp.constitution
labels: ["constitution", "phase3", "chatbot", "mcp", "integration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

# /sp.constitution

## ROLE & OBJECTIVE
You are an Expert AI Full-Stack Architect building **Phase III: Todo AI Chatbot**.
**CRITICAL CONTEXT:** You are NOT building a completely new isolated app. You are building a **Conversational Interface** (Phase 3) that sits alongside the existing **Web Interface** (Phase 2).

## INTEGRATION & COMPATIBILITY RULES
1.  **Shared "Reality":** Both Phase 2 and Phase 3 connect to the **same Neon PostgreSQL database**.
2.  **Data Compatibility:** You MUST read `todo-phase-2/backend/app/models.py` first. Your Phase 3 SQLModel classes must be an **exact mirror** of Phase 2 so that a task created in the Chatbot (Phase 3) is immediately visible in the Web Dashboard (Phase 2).
3.  **Non-Destructive:** You are forbidden from altering the Database Schema in a way that would break the existing Phase 2 application.
4.  **Code Separation:** While the *data* is shared, the *code* is separate. Do not import files across folders (to avoid path errors). Instead, replicate the Model definitions inside `todo-phase-3` to match Phase 2 exactly.

## AGENTIC RESOURCES
* **System Capabilities:** You are authorized to use all Agents, Skills, and Tools defined in the root `.claude` folder.
* **User Context:** You are assisting **Muhammad Haris Awan** (CEO). The system should reflect high-quality, enterprise-grade architecture suitable for a CEO's workflow.

## TECHNOLOGY STACK (Phase 3 Specific)
* **Frontend:** OpenAI ChatKit (Next.js)
* **Backend:** Python FastAPI + OpenAI Agents SDK
* **Brain:** MCP Server (Official SDK)
* **Database:** Neon (Shared instance)

## ARCHITECTURAL BLUEPRINT
1.  **The MCP Server:** Implements `add_task`, `list_tasks`, etc. These tools perform CRUD operations on the shared database.
2.  **The Agent:** Stateless. It creates a plan based on user input, calls the MCP tools, and returns a natural language summary.
3.  **The Flow:**
    User: "Add call with Asya to my list" -> Agent -> MCP Tool (creates row in DB) -> DB confirms -> Agent: "Added." -> (User checks Phase 2 Web App

## Response snapshot

Created constitution v1.0.0 for Phase III: Todo AI Chatbot with 6 core principles:

1. **Data Compatibility First** - SQLModel definitions MUST mirror Phase 2 exactly
2. **Non-Destructive Schema Policy** - No breaking changes to shared database
3. **Code Separation** - Replicate models, don't import across phases
4. **MCP-First Architecture** - All CRUD via MCP tools, Agent doesn't access DB directly
5. **Stateless Agent Design** - No conversation memory, context passed explicitly
6. **Enterprise-Grade Quality** - Proper error handling, logging, env vars for secrets

Technology stack documented: ChatKit (Next.js) → FastAPI + OpenAI Agents SDK → MCP Server → Neon PostgreSQL

## Outcome

- ✅ Impact: Constitution created establishing Phase 3 development governance
- 🧪 Tests: N/A (governance document)
- 📁 Files: `.specify/memory/constitution.md` created
- 🔁 Next prompts: `/sp.specify` to create feature spec, `/sp.plan` to create implementation plan
- 🧠 Reflection: User provided clear architectural vision; constitution captures integration constraints well

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
