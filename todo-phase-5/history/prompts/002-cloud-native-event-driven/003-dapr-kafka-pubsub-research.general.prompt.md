---
id: 003
title: Dapr Kafka Pub/Sub Research
stage: general
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 002-cloud-native-event-driven
branch: 002-cloud-native-event-driven
user: architect
command: research
labels: ["dapr", "kafka", "pubsub", "strimzi", "redpanda", "cloudevents", "schema-versioning", "dead-letter"]
links:
  spec: specs/002-cloud-native-event-driven/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - history/prompts/002-cloud-native-event-driven/003-dapr-kafka-pubsub-research.general.prompt.md
tests:
  - none (research deliverable)
---

## Prompt

Research Dapr Pub/Sub with Apache Kafka. I need to know:
1. Dapr component YAML configuration for Kafka (pubsub.kafka)
2. How to configure topics, consumer groups, and partitions
3. How to publish events from FastAPI via Dapr HTTP API
4. How to subscribe to topics (programmatic vs declarative subscriptions)
5. Message routing and CloudEvents format
6. Dead letter topics configuration
7. Strimzi Kafka operator setup on Kubernetes vs Redpanda Cloud comparison
8. Best practices for event schema versioning with Dapr Pub/Sub

Search the official Dapr docs. Report with concrete YAML and Python code examples.

## Response snapshot

Delivered comprehensive research report covering all 8 areas with concrete YAML and Python code examples:
1. Full Dapr pubsub.kafka component YAML with all metadata fields (brokers, auth, TLS, consumer config, producer config, schema registry)
2. Topic mapping for DoneKaro (task-events, reminders, task-updates) with Strimzi KafkaTopic CRDs and partition key strategy
3. Complete FastAPI publisher implementation using Dapr HTTP API (httpx, no direct Kafka client) with bulk publish support
4. Both declarative (K8s CRDs with CEL routing rules) and programmatic (/dapr/subscribe) subscription patterns with recommendation for declarative
5. CloudEvents 1.0 format details, CEL routing expressions, event type taxonomy for DoneKaro
6. Dead letter topic configuration (declarative + programmatic) with DLQ consumer pattern and SUCCESS/RETRY/DROP status handling
7. Side-by-side Strimzi vs Redpanda Cloud comparison with full Strimzi Kafka CRD for both production (3-broker HA) and Minikube (1-broker ephemeral)
8. Schema versioning strategy using Pydantic + CloudEvents type versioning with backward compatibility rules and event catalog pattern

## Outcome

- Impact: Research deliverable providing architectural foundation for Dapr Pub/Sub implementation across all three services
- Tests: none (research deliverable)
- Files: 1 file created (this PHR)
- Next prompts: /sp.plan to create the architectural plan incorporating these Dapr Pub/Sub patterns, or /sp.adr for Strimzi vs Redpanda decision
- Reflection: Web fetch was unavailable; report drawn from training knowledge of Dapr docs. All patterns align with constitution Principle III (Dapr sidecar abstraction) and FR-012 (Dapr Pub/Sub for all messaging).

## Evaluation notes (flywheel)

- Failure modes observed: WebSearch and WebFetch tools were unavailable (auto-denied); fell back to training knowledge
- Graders run and results (PASS/FAIL): Manual review required -- recommend verifying against docs.dapr.io for any API changes post May 2025
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Verify Dapr bulk publish API path is still v1.0-alpha1 in the target Dapr runtime version
