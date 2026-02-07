# Research: Cloud-Native Event-Driven Task System

**Branch**: `002-cloud-native-event-driven` | **Date**: 2026-02-06
**Purpose**: Resolve all NEEDS CLARIFICATION items from plan.md Technical Context

---

## R1: Dapr State Management — PostgreSQL v1 vs v2

### Decision: Use `state.postgresql` v2

### Rationale
- **v2** uses parameterized queries (SQL injection resistant) and stores values as `bytea` (binary).
- **v1** stores values as JSONB and supports the Dapr Query API for filtering/sorting.
- v2 is the recommended version by the Dapr team for new projects.
- The **Query API is NOT available on v2** — this is the critical trade-off.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| v1 (JSONB + Query API) | Supports rich queries (EQ, IN, GT, sort, pagination) | Deprecated path; SQL injection risk from string interpolation |
| v2 (bytea + no Query API) | Secure parameterized queries; recommended by Dapr | No Query API; must implement index-key pattern for lookups |

### Impact on Architecture

Since v2 lacks the Query API, we use an **index-key pattern**:
- Maintain index keys like `chat-api||task-index||{user-id}` containing a list of task IDs belonging to that user.
- Use **bulk get** (`POST /v1.0/state/{store}/bulk`) to fetch multiple tasks by their IDs.
- Use **transactions** (`POST /v1.0/state/{store}/transaction`) to atomically update both the task data and the index key.

**Example — List user's tasks**:
1. `GET /v1.0/state/statestore-postgres/chat-api||task-index||user-123` → returns `["task-abc", "task-def", "task-ghi"]`
2. `POST /v1.0/state/statestore-postgres/bulk` with `{"keys": ["chat-api||task||task-abc", "chat-api||task||task-def", "chat-api||task||task-ghi"]}`
3. Returns all task objects in a single round-trip.

### Key Technical Details

**State Key Auto-Prefixing**: Dapr automatically prefixes keys with `{app-id}||`. So if app-id is `chat-api` and you save key `task||abc123`, the actual stored key is `chat-api||task||abc123`. This matches our constitution's key pattern.

**ETags (Optimistic Locking)**:
- Every state entry has a UUID-based ETag returned on read.
- Set `concurrency: first-write` in save metadata to enforce ETag checking.
- On mismatch → Dapr returns HTTP 409 Conflict.
- Read-modify-write pattern:
  ```python
  # Read with ETag
  resp = await client.get(f"{DAPR_URL}/v1.0/state/{store}/{key}")
  etag = resp.headers.get("ETag")
  data = resp.json()

  # Save with ETag (optimistic lock)
  await client.post(f"{DAPR_URL}/v1.0/state/{store}", json=[{
      "key": key,
      "value": modified_data,
      "etag": etag,
      "options": {"concurrency": "first-write"}
  }])
  ```

**Bulk Operations**:
- Bulk save: `POST /v1.0/state/{store}` with array body `[{key, value, etag}, ...]`
- Bulk get: `POST /v1.0/state/{store}/bulk` with `{"keys": ["key1", "key2"]}`

**Transactions**:
- `POST /v1.0/state/{store}/transaction` with `upsert` and `delete` operations.
- Entire transaction rolls back on any ETag mismatch.
- Used for atomic index + data updates.

**TTL Support**:
- Set via `metadata.ttlInSeconds` on individual save operations.
- PostgreSQL cleanup runs on `cleanupInterval` (default 1 hour).
- Useful for conversation session TTL (4 hours recommended).

**Component Configuration (v2)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore-postgres
  namespace: donekaro
spec:
  type: state.postgresql.v2
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-credentials
        key: connection-string
    - name: tableName
      value: "dapr_state"
    - name: metadataTableName
      value: "dapr_metadata"
    - name: cleanupIntervalInSeconds
      value: "3600"
  auth:
    secretStore: kubernetes-secrets
```

### Conversation History Best Practices
- TTL on active sessions (4 hours) to auto-expire stale conversations.
- Message trimming: keep max 50 messages per conversation to bound state size.
- Index keys for user sessions: `chat-api||conversation-index||{user-id}` → list of active session IDs.
- Hot/cold separation: active sessions in Dapr state store, completed conversations archived via Kafka events.

---

## R2: Dapr Pub/Sub with Apache Kafka

### Decision: Use `pubsub.kafka` with Strimzi (local) and Redpanda Cloud (production)

### Rationale
- Dapr's `pubsub.kafka` component abstracts all Kafka client interactions behind the Dapr HTTP API.
- Application code calls `POST /v1.0/publish/{pubsub}/{topic}` — zero Kafka client imports (Constitution III).
- Strimzi provides a production-grade Kafka operator for Kubernetes that's free and well-maintained.
- Redpanda Cloud offers a Kafka-compatible managed service that eliminates operational overhead in production.
- **Crucially**: Switching between Strimzi and Redpanda requires only a Dapr component YAML change — application code is identical.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| Strimzi everywhere | Free, consistent across environments | Operational overhead in production (monitoring, upgrades, scaling) |
| Redpanda Cloud everywhere | Zero ops, managed | Cost; not free for local dev |
| Confluent Cloud | Enterprise support, Schema Registry | Higher cost; Schema Registry not needed with Dapr CloudEvents |
| Strimzi local + Redpanda Cloud prod | Best of both: free local, managed prod | Different brokers per env (mitigated by Dapr abstraction) |

### Component Configuration

**Local (Strimzi)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: donekaro
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "{app-id}-group"
    - name: authType
      value: "none"
    - name: initialOffset
      value: "oldest"
    - name: maxMessageBytes
      value: "1048576"
    - name: consumeRetryInterval
      value: "1000ms"
    - name: requiredAcks
      value: "all"
    - name: disableTls
      value: "true"
```

**Production (Redpanda Cloud)**:
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: pubsub-kafka
  namespace: donekaro
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      secretKeyRef:
        name: kafka-credentials
        key: brokers
    - name: consumerGroup
      value: "{app-id}-group"
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-credentials
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-credentials
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: initialOffset
      value: "oldest"
    - name: requiredAcks
      value: "all"
    - name: disableTls
      value: "false"
  auth:
    secretStore: kubernetes-secrets
```

### Publishing Events (Python/FastAPI)

```python
import httpx
from datetime import datetime, timezone
import uuid

DAPR_URL = f"http://localhost:{DAPR_HTTP_PORT}"

async def publish_task_event(topic: str, event_type: str, data: dict):
    """Publish event with explicit CloudEvents envelope."""
    event = {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "chat-api",
        "type": f"com.donekaro.{event_type}",
        "datacontenttype": "application/json",
        "time": datetime.now(timezone.utc).isoformat(),
        "data": data
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DAPR_URL}/v1.0/publish/pubsub-kafka/{topic}",
            json=event,
            headers={"Content-Type": "application/cloudevents+json"}
        )
        resp.raise_for_status()
```

### Subscriptions — Declarative (Recommended)

Use Kubernetes CRDs (`dapr.io/v2alpha1`) with CEL-based routing rules:

```yaml
apiVersion: dapr.io/v2alpha1
kind: Subscription
metadata:
  name: recurring-engine-task-events
spec:
  pubsubname: pubsub-kafka
  topic: task-events
  routes:
    rules:
      - match: event.type == "com.donekaro.task.completed"
        path: /events/task-completed
      - match: event.type == "com.donekaro.task.created"
        path: /events/task-created
      - match: event.type == "com.donekaro.task.updated"
        path: /events/task-updated
    default: /events/task-events
  scopes:
    - recurring-engine
```

### Dead Letter Topics

Per-subscription dead letter configuration for failed message processing:

```yaml
spec:
  deadLetterTopic: "dead-letter-task-events"
```

Handler responses control retry behavior:
- Return `SUCCESS` → message acknowledged
- Return `RETRY` → message redelivered after `consumeRetryInterval`
- Return `DROP` → message sent to dead letter topic

**Recommendation**: Set 30-day retention on dead letter topics for investigation.

### Partition Key Strategy

Use `taskId` as the Kafka partition key to ensure per-task event ordering:

```python
# Metadata for ordered publishing
headers = {
    "Content-Type": "application/cloudevents+json",
    "metadata.partitionKey": task_id  # Ensures per-task ordering
}
```

### Event Schema Versioning

- Use CloudEvents `type` field for versioning: `com.donekaro.task.created.v1`
- **Additive-only** evolution: new fields can be added, existing fields never removed or renamed.
- All consumers must tolerate unknown fields (Pydantic `model_config = ConfigDict(extra="ignore")`).
- Breaking changes require a new event type version and a migration period.

---

## R3: Dapr Jobs API (alpha1)

### Decision: Use Dapr Jobs API for all scheduling (recurring triggers + due-date reminders)

### Rationale
- Constitution Principle IV mandates Dapr Jobs API — no cron polling, sleep timers, or OS cron.
- The Jobs API is in alpha1 status, meaning the API surface may change.
- We abstract job registration behind a `job_service.py` layer to isolate the alpha API surface.

### API Surface

**Register a Job**:
```
PUT http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job-name}
Content-Type: application/json

{
  "schedule": "@every 24h",           // Cron syntax OR @every duration
  "repeats": 0,                        // 0 = indefinite; N = fire N times
  "dueTime": "2026-02-07T16:30:00Z",  // For one-shot jobs
  "ttl": "48h",                        // Optional: auto-delete after TTL
  "data": {                            // Arbitrary JSON payload
    "taskId": "uuid",
    "type": "recurrence-trigger",
    "userId": "user-uuid"
  }
}
```

**Get Job Status**:
```
GET http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job-name}
```

**Delete (Cancel) a Job**:
```
DELETE http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job-name}
```

**Job Callback**: When a job fires, Dapr sends:
```
PUT http://{app}/job/{job-name}

Body: { "data": { ... } }  // The data payload from registration
```

The recurring-engine must expose:
```python
@app.put("/job/{job_name}")
async def handle_job_callback(job_name: str, request: Request):
    payload = await request.json()
    job_type = payload["data"]["type"]

    if job_type == "recurrence-trigger":
        await handle_recurrence(payload["data"])
    elif job_type == "reminder-fired":
        await handle_reminder(payload["data"])
```

### Cron Schedule Formats Supported

| Format | Example | Meaning |
|--------|---------|---------|
| Standard cron | `0 9 * * 1-5` | Weekdays at 9 AM |
| @every | `@every 24h` | Every 24 hours |
| @daily | `@daily` | Once per day (midnight) |
| @weekly | `@weekly` | Once per week |
| @monthly | `@monthly` | Once per month |

### Job Naming Convention

Pattern: `{type}-{task-id}`
- `recurrence-{taskId}` — Recurring task trigger
- `reminder-{taskId}` — Due-date reminder
- `reminder-{taskId}-{level}` — Multi-level reminders (e.g., 1h-before, 30m-before)

### Fallback Strategy

If Dapr Jobs API proves unstable in alpha1:
- **Primary fallback**: Dapr Input Bindings with `bindings.cron` component.
- Cron bindings trigger at intervals, and the recurring-engine polls its state store for due jobs.
- This is less efficient (polling vs push) but stable (GA).

```yaml
# Fallback: Cron binding (only if Jobs API is unusable)
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: cron-check
spec:
  type: bindings.cron
  version: v1
  metadata:
    - name: schedule
      value: "@every 1m"
    - name: direction
      value: "input"
```

### Known Limitations (alpha1)
- API path includes `v1.0-alpha1` — will change when promoted to stable.
- Job persistence depends on the Dapr scheduler service (runs as a separate system service in Dapr 1.14+).
- No built-in distributed locking for job execution across replicas — must handle idempotency in the callback handler.
- Limited observability: job execution metrics not yet integrated into Dapr metrics endpoint.

### Idempotency Handling

Since Jobs API may deliver callbacks more than once (at-least-once delivery):
```python
async def handle_recurrence(data: dict):
    task_id = data["taskId"]
    idempotency_key = f"job-processed||{task_id}||{data.get('instanceId', '')}"

    # Check if already processed
    existing = await state_client.get("statestore-postgres", idempotency_key)
    if existing:
        logger.info("Duplicate job callback, skipping", task_id=task_id)
        return

    # Process and mark as handled
    await generate_next_instance(task_id)
    await state_client.save("statestore-postgres", idempotency_key, {
        "processedAt": datetime.now(timezone.utc).isoformat()
    }, metadata={"ttlInSeconds": "86400"})  # 24h TTL
```

---

## R4: Strimzi Kafka Operator vs Redpanda Cloud

### Decision: Strimzi for local (Minikube), Redpanda Cloud for production

### Rationale
- **Strimzi** is the standard Kafka operator for Kubernetes, free and open-source.
- Running self-managed Kafka in production requires dedicated expertise (broker tuning, partition rebalancing, monitoring, upgrades).
- **Redpanda Cloud** is Kafka API-compatible, managed, and eliminates operational overhead.
- Dapr's `pubsub.kafka` component works identically with both — only broker addresses and auth config change.

### Alternatives Considered

| Option | Ops Cost | Financial Cost | Kafka Compatibility | Decision |
|--------|----------|---------------|---------------------|----------|
| Strimzi (local + prod) | High in prod | Free | 100% (is Kafka) | Rejected for prod ops cost |
| Redpanda Cloud (everywhere) | Zero | ~$100+/mo | 99.9% | Rejected for local cost |
| Confluent Cloud | Zero | Higher | 100% | Rejected for cost |
| **Strimzi local + Redpanda prod** | Low (local only) | Moderate | Both Kafka-compatible | **Selected** |

### Local Strimzi Setup (Minikube)

```yaml
# Strimzi Kafka cluster for local dev (single broker, ephemeral)
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: kafka-cluster
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
    storage:
      type: ephemeral
    config:
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
```

**Topic Definitions**:
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: "604800000"      # 7 days
    cleanup.policy: "delete"
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: "259200000"      # 3 days
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: kafka-cluster
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: "86400000"       # 1 day
```

---

## R5: Frontend Real-Time Updates — SSE vs WebSocket

### Decision: Server-Sent Events (SSE) via chat-api bridge

### Rationale
- SSE is unidirectional (server → client), which matches the task-update broadcast pattern.
- Simpler than WebSocket: native browser `EventSource` API, auto-reconnect, `Last-Event-ID` support.
- chat-api subscribes to `task-updates` Kafka topic via Dapr and bridges events to SSE clients.
- WebSocket would add bidirectional complexity not needed for read-only update streams.

### Alternatives Considered

| Option | Pros | Cons |
|--------|------|------|
| **SSE bridge in chat-api** | Simple, auto-reconnect, unidirectional, native browser API | One-way only; connection per user |
| WebSocket | Bidirectional, efficient | Over-engineered for broadcast; more complex reconnect logic |
| Long polling | Simplest server-side | Higher latency, more HTTP overhead |
| Dapr Pub/Sub → Frontend directly | No bridge needed | Frontend can't use Dapr sidecar (runs in browser) |

### Implementation Pattern

**chat-api SSE endpoint**:
```python
from fastapi import Request
from fastapi.responses import StreamingResponse
import asyncio

# In-memory map of user_id → list of asyncio.Queue
sse_connections: dict[str, list[asyncio.Queue]] = {}

@app.get("/events/stream")
async def sse_stream(request: Request, user_id: str):
    queue = asyncio.Queue()
    sse_connections.setdefault(user_id, []).append(queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"id: {event['id']}\nevent: task-update\ndata: {json.dumps(event['data'])}\n\n"
        except asyncio.TimeoutError:
            yield f": keepalive\n\n"  # SSE comment as heartbeat
        finally:
            sse_connections[user_id].remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

**Frontend SSE client**:
```typescript
// lib/sse-client.ts
export function connectTaskUpdates(userId: string, onUpdate: (data: TaskUpdate) => void) {
    const source = new EventSource(`/api/events/stream?userId=${userId}`);
    source.addEventListener('task-update', (event) => {
        const data = JSON.parse(event.data);
        onUpdate(data);
    });
    source.onerror = () => {
        // EventSource auto-reconnects; log for observability
        console.warn('SSE connection error, reconnecting...');
    };
    return source; // caller can close with source.close()
}
```

### Scalability Consideration

- SSE connections are in-memory per chat-api pod instance.
- On pod restart, clients auto-reconnect via `EventSource` built-in retry.
- Each pod runs its own Dapr Pub/Sub consumer (Kafka consumer group: `chat-api-group`), so events are distributed across pods.
- A user connected to Pod A will receive events processed by Pod A. If a task change is processed by Pod B, that user won't see it via SSE.
- **Mitigation**: Use a shared Kafka consumer group + broadcast to all pods, or accept eventual consistency (client polls on reconnect).

---

## R6: Dapr Secrets API — Local vs Kubernetes

### Decision: `secretstores.local.file` for local dev, `secretstores.kubernetes` for production

### Rationale
- Local development doesn't run in Kubernetes, so Kubernetes Secrets are unavailable.
- Dapr supports a local file-based secret store for development.
- Production uses Kubernetes Secrets as mandated by Constitution Principle VI.

### Local Secret Store Configuration

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: local-secrets
spec:
  type: secretstores.local.file
  version: v1
  metadata:
    - name: secretsFile
      value: "./secrets.json"
    - name: nestedSeparator
      value: ":"
```

**secrets.json** (gitignored):
```json
{
  "postgres-credentials": {
    "connection-string": "host=localhost port=5432 user=dapr password=dapr dbname=donekaro sslmode=disable"
  },
  "gemini-credentials": {
    "api-key": "your-gemini-api-key-here"
  },
  "vapid-credentials": {
    "public-key": "your-vapid-public-key",
    "private-key": "your-vapid-private-key",
    "mailto": "mailto:admin@donekaro.app"
  },
  "auth-credentials": {
    "jwt-secret": "your-jwt-secret-here"
  }
}
```

### Access Pattern (Same for Both Stores)

```python
# Works identically for local.file and kubernetes secret stores
resp = await client.get(f"{DAPR_URL}/v1.0/secrets/{store_name}/{secret_name}")
secret = resp.json()  # {"api-key": "value"}
```

---

## Summary of Decisions

| # | Topic | Decision | Risk Level |
|---|-------|----------|------------|
| R1 | State Store Version | PostgreSQL v2 (bytea, no Query API) | Medium — requires index-key pattern |
| R2 | Pub/Sub Broker | Strimzi local, Redpanda Cloud prod | Low — Dapr abstracts broker differences |
| R3 | Scheduling | Dapr Jobs API alpha1 with cron-binding fallback | High — alpha API may change |
| R4 | Kafka Selection | Strimzi + Redpanda split by environment | Low |
| R5 | Real-Time Frontend | SSE bridge in chat-api | Low — simple, well-supported |
| R6 | Secrets Management | Local file dev, K8s Secrets prod | Low — standard Dapr pattern |

---

## ADR Suggestions

Two architecturally significant decisions warrant formal ADRs:

1. **PostgreSQL State Store v1 vs v2**: Impacts all query patterns across every service. The index-key workaround for lacking Query API is a cross-cutting pattern.
   > Run `/sp.adr dapr-postgresql-state-store-version-selection`

2. **Kafka Broker Selection (Strimzi vs Redpanda Cloud)**: Long-term infrastructure decision with operational and cost implications.
   > Run `/sp.adr kafka-broker-selection`
