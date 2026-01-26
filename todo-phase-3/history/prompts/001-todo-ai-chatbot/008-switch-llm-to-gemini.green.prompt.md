---
id: 008
title: Switch LLM to Google Gemini
stage: green
date: 2026-01-26
surface: agent
model: claude-opus-4-5-20251101
feature: 001-todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: system
command: /sp.implement
labels: ["refactor", "llm", "gemini", "litellm", "integration"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/requirements.txt
  - backend/app/config.py
  - backend/app/agent/runner.py
  - backend/.env.example
  - backend/.env
tests:
  - Manual: List tasks (empty)
  - Manual: Add task "Buy groceries"
  - Manual: List tasks (shows task)
  - Manual: Complete task
---

## Prompt

/sp.implement

**Context:**
The Phase 3 application is fully built. The MCP Server, Database connection, and ChatKit frontend are ready.
**Problem:** The current implementation uses the default OpenAI Model (`gpt-4o`), but the user does not have a paid OpenAI API Key.
**Goal:** Switch the AI Engine to **Google Gemini 2.5 Flash** using the `litellm` integration.

**Action Plan:**
1. Update Dependencies: Add `litellm` and `google-generativeai`
2. Refactor Agent Configuration: Update to use LiteLLM with Gemini model

## Response snapshot

Successfully migrated from OpenAI to Google Gemini 2.5 Flash using LiteLLM.

**Changes implemented:**
1. **requirements.txt**: Added `litellm>=1.30.0` and `google-generativeai>=0.5.0`
2. **app/config.py**: Added `gemini_api_key`, `openai_api_key` (optional), and `llm_model` settings
3. **app/agent/runner.py**: Replaced OpenAI client with `litellm.completion()` calls
4. **.env.example**: Updated with Gemini configuration options
5. **.env**: Set `LLM_MODEL=gemini/gemini-2.5-flash`

**Verified functionality:**
- List tasks: Working
- Add task: Working
- Complete task: Working
- Conversation persistence: Working
- Tool calling with Gemini: Working

**Note:** Free tier has 5 requests/minute limit per model.

## Outcome

- Impact: Successfully migrated LLM provider from OpenAI to Google Gemini, enabling free-tier usage
- Tests: All manual tests passed (list, add, complete tasks via chat)
- Files: 5 files modified (requirements.txt, config.py, runner.py, .env.example, .env)
- Next prompts: Start frontend, test full end-to-end flow
- Reflection: LiteLLM provides seamless multi-provider support with minimal code changes

## Evaluation notes (flywheel)

- Failure modes observed: Rate limiting on free tier (5 req/min); model name changes between API versions
- Graders run and results (PASS/FAIL): Manual verification PASS
- Prompt variant (if applicable): Standard /sp.implement with context
- Next experiment (smallest change to try): Add retry logic with exponential backoff for rate limits
