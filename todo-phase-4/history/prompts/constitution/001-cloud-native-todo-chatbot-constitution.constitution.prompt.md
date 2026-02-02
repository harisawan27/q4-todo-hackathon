---
id: 001
title: Cloud-Native Todo Chatbot Constitution
stage: constitution
date: 2025-02-02
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: 001-todo-ai-chatbot
user: student
command: /sp.constitution
labels: ["constitution", "cloud-native", "kubernetes", "docker", "sdd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - frontend/ (copied from ../todo-phase-3)
  - backend/ (copied from ../todo-phase-3)
  - history/prompts/constitution/
  - history/prompts/general/
  - specs/
tests:
  - null
---

## Prompt

# GIAIC Phase 4 Constitution: Cloud-Native Todo Chatbot

I am a student at GIAIC, and this is the "Spec-Driven Development" (SDD) phase for my project. You are my Agentic DevOps Engineer.

## Context:
- Source Code: The AI Chatbot is located in `../todo-phase-3`.
- Architecture: The chatbot consists of a frontend and a backend that need to be containerized and deployed.
- Cluster: Local Kubernetes (Minikube).

## Rules of Engagement:
1. STRICT NO MANUAL CODING: You must generate all files, scripts, and configurations. I will not edit code myself.
2. SDD WORKFLOW: Write `spec.md` -> Generate `plan.md` -> Break into tasks -> Implement.
3. TOOLING:
   - Use 'Gordon' (Docker AI) instructions for containerization.
   - Use 'kubectl-ai' or 'Kagent' for Kubernetes manifests and Helm charts.
   - Use 'Minikube' as the deployment target.

## Task 1: Initialization & Analysis
1. Create `frontend/` and `backend/` directories within `todo-phase-4`.
2. Copy the relevant chatbot source code from `../todo-phase-3` into th

## Response snapshot

Created the GIAIC Phase 4 Cloud-Native Todo Chatbot Constitution with six core principles:

1. **SDD (Spec-Driven Development)**: All features follow spec → plan → tasks → implement workflow
2. **Zero Manual Coding**: AI agent generates all files, student does not code manually
3. **Containerization-First**: Docker with Gordon AI, multi-stage builds, non-root users
4. **Kubernetes-Native Deployment**: Minikube target, kubectl-ai/Kagent for manifests
5. **Environment Parity**: Dev/staging/prod consistency via externalized config
6. **Observability & Debuggability**: Health checks, structured logging, metrics

Also completed Task 1 initialization:
- Created `frontend/` and `backend/` directories
- Copied source code from `../todo-phase-3` (Next.js frontend, FastAPI backend)
- Created `history/prompts/` directory structure
- Created `specs/` directory for feature specifications

Constitution version: 1.0.0 (initial ratification)

## Outcome

- ✅ Impact: Constitution established, project initialized with source code
- 🧪 Tests: N/A (constitution document)
- 📁 Files: constitution.md, frontend/, backend/, history/prompts/
- 🔁 Next prompts: /sp.specify for containerization feature, /sp.plan for implementation
- 🧠 Reflection: Clean initialization following SDD principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with /sp.specify for containerization
