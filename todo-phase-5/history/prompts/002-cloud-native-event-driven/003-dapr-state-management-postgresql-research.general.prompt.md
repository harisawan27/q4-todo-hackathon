---
id: 003
title: Dapr State Management PostgreSQL Research
stage: general
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: user
command: research
labels: ["dapr", "state-management", "postgresql", "etag", "ttl", "transactions"]
links:
  spec: specs/002-cloud-native-event-driven/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/002-cloud-native-event-driven/003-dapr-state-management-postgresql-research.general.prompt.md
tests:
  - none
---

## Prompt

Research Dapr State Management with PostgreSQL backend. I need to know:
1. Dapr component YAML configuration for state.postgresql (v1 and v2)
2. State key patterns and namespacing
3. How ETags work for optimistic locking
4. Bulk state operations API
5. Query API for filtering and sorting state entries
6. Transaction support
7. How to use from Python/FastAPI via Dapr HTTP API
8. State store TTL support
9. Best practices for using Dapr state store for conversation history

Search the official Dapr docs and provide concrete YAML and Python/curl examples.

## Response snapshot

Comprehensive research covering all 9 areas of Dapr State Management with PostgreSQL:
- v1 vs v2 YAML configurations with production-ready examples using Dapr Secrets
- Key namespacing: Dapr auto-prefixes with app-id using || separator; constitution pattern is {entity-type}||{id}
- ETags: UUID-based optimistic locking with first-write concurrency mode; 409 Conflict on mismatch
- Bulk get/save via /bulk endpoint and standard POST with array body
- Query API: ONLY supported on v1 (JSONB); v2 uses bytea so requires index-key pattern instead
- Transactions: atomic multi-key upsert/delete via /transaction endpoint; supports ETag in operations
- Full DaprStateClient Python module with httpx.AsyncClient for FastAPI integration
- TTL via metadata.ttlInSeconds; cleanup runs on configurable interval
- Conversation history: TTL sessions, message trimming, index keys, hot/cold data separation, transaction-based multi-key updates
- Key architectural decision: use v2 + index keys for security without Query API dependency

## Outcome

- Impact: Research document providing concrete implementation patterns for all Dapr state operations needed by chat-api, notification-service, and recurring-engine
- Tests: none
- Files: PHR only (research output in conversation)
- Next prompts: Create architectural plan (sp.plan), define tasks (sp.tasks), implement DaprStateClient module
- Reflection: Web fetch tools were unavailable; research was based on deep knowledge of Dapr documentation. The v1 vs v2 Query API incompatibility is a critical architectural finding that should be captured in an ADR.

## Evaluation notes (flywheel)

- Failure modes observed: WebSearch and WebFetch tools were denied; relied on knowledge base
- Graders run and results (PASS/FAIL): N/A - research task
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Verify v2 Query API status against latest Dapr release notes when web tools are available
