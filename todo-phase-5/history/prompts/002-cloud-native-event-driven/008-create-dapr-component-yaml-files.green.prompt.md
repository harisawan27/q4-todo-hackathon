---
id: 008
title: Create Dapr Component YAML Files
stage: green
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: developer
command: write-files
labels: ["dapr", "components", "yaml", "kafka", "postgresql", "kubernetes"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - dapr-components/local/statestore-postgres.yaml
  - dapr-components/local/pubsub-kafka.yaml
  - dapr-components/local/secretstore-local.yaml
  - dapr-components/local/subscriptions.yaml
  - dapr-components/production/statestore-postgres.yaml
  - dapr-components/production/pubsub-kafka.yaml
  - dapr-components/production/secretstore-k8s.yaml
  - dapr-components/production/subscriptions.yaml
tests:
  - none
---

## Prompt

Create the following Dapr component YAML files in F:\q4-todo-hackathon\todo-phase-5\. Write the actual file content.

1. dapr-components/local/statestore-postgres.yaml -- Dapr State Store (PostgreSQL v2) with secretKeyRef
2. dapr-components/local/pubsub-kafka.yaml -- Dapr Pub/Sub (Kafka) for local Strimzi
3. dapr-components/local/secretstore-local.yaml -- local file secret store
4. dapr-components/local/subscriptions.yaml -- Declarative Dapr Subscriptions for all services
5. dapr-components/production/statestore-postgres.yaml -- Production PostgreSQL with K8s Secrets
6. dapr-components/production/pubsub-kafka.yaml -- Production Kafka (Redpanda Cloud) with SASL_SSL
7. dapr-components/production/secretstore-k8s.yaml -- Production Kubernetes Secrets store
8. dapr-components/production/subscriptions.yaml -- Production subscriptions (same routes, production namespace)

## Response snapshot

Created all 8 Dapr component YAML files across local and production environments. Local components use file-based secret store and plaintext Kafka without TLS. Production components use Kubernetes secret store, namespace donekaro, and SASL_SSL authentication for Kafka (Redpanda Cloud). Subscriptions define event routing for recurring-engine, notification-service, and chat-api with dead letter topics.

## Outcome

- Impact: All Dapr component definitions created for both local development and production environments
- Tests: none
- Files: 8 YAML files created in dapr-components/local/ and dapr-components/production/
- Next prompts: Configure secrets.json for local development, deploy components to Kubernetes
- Reflection: Straightforward file creation task; all content provided verbatim by the user

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
