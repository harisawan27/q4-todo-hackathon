# Quickstart: DoneKaro Cloud-Native Event-Driven System

**Branch**: `002-cloud-native-event-driven` | **Date**: 2026-02-06

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | 24+ | [docker.com](https://www.docker.com/products/docker-desktop/) |
| Minikube | 1.32+ | `winget install minikube` / `brew install minikube` |
| kubectl | 1.28+ | `winget install kubectl` / `brew install kubectl` |
| Helm | 3.14+ | `winget install helm` / `brew install helm` |
| Dapr CLI | 1.14+ | `winget install Dapr.CLI` / `brew install dapr/tap/dapr-cli` |
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Node.js | 20+ | [nodejs.org](https://nodejs.org/) |

---

## Option A: Full Kubernetes (Minikube) Setup

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
minikube addons enable ingress
```

### 2. Install Dapr on Kubernetes

```bash
dapr init -k --wait
# Verify Dapr is running
dapr status -k
```

Expected output: `dapr-operator`, `dapr-sentry`, `dapr-sidecar-injector`, `dapr-placement`, `dapr-scheduler` all running.

### 3. Install Strimzi Kafka Operator

```bash
# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl create -f 'https://strimzi.io/install/latest?namespace=kafka' -n kafka

# Wait for operator to be ready
kubectl wait --for=condition=Ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

### 4. Deploy Kafka Cluster

```bash
# Apply Kafka cluster and topic CRDs
kubectl apply -f k8s-manifests/base/infrastructure/kafka/kafka-cluster.yaml -n kafka
kubectl apply -f k8s-manifests/base/infrastructure/kafka/kafka-topics.yaml -n kafka

# Wait for Kafka to be ready (takes 2-3 minutes)
kubectl wait kafka/kafka-cluster --for=condition=Ready --timeout=300s -n kafka
```

### 5. Create Application Namespace and Secrets

```bash
# Create namespace
kubectl create namespace donekaro

# Create secrets (replace placeholder values)
kubectl create secret generic postgres-credentials \
  --from-literal=connection-string="host=YOUR_NEON_HOST port=5432 user=YOUR_USER password=YOUR_PASSWORD dbname=donekaro sslmode=require" \
  -n donekaro

kubectl create secret generic gemini-credentials \
  --from-literal=api-key="YOUR_GEMINI_API_KEY" \
  -n donekaro

kubectl create secret generic vapid-credentials \
  --from-literal=public-key="YOUR_VAPID_PUBLIC_KEY" \
  --from-literal=private-key="YOUR_VAPID_PRIVATE_KEY" \
  --from-literal=mailto="mailto:you@example.com" \
  -n donekaro

kubectl create secret generic auth-credentials \
  --from-literal=jwt-secret="YOUR_JWT_SECRET" \
  -n donekaro
```

### 6. Apply Dapr Components

```bash
kubectl apply -f dapr-components/local/ -n donekaro
```

### 7. Build and Deploy Services

```bash
# Point Docker to Minikube's registry
eval $(minikube docker-env)   # Linux/Mac
# On Windows PowerShell:
# & minikube -p minikube docker-env --shell powershell | Invoke-Expression

# Build all service images
docker build -t donekaro/chat-api:latest services/chat-api/
docker build -t donekaro/notification-service:latest services/notification-service/
docker build -t donekaro/recurring-engine:latest services/recurring-engine/
docker build -t donekaro/frontend:latest frontend/

# Deploy with Kustomize
kubectl apply -k k8s-manifests/overlays/local/
```

### 8. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n donekaro

# Check Dapr sidecars are injected
kubectl get pods -n donekaro -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{range .spec.containers[*]}{.name}{", "}{end}{"\n"}{end}'

# Check Dapr components
dapr components -k -n donekaro
```

### 9. Access the Application

```bash
# Port-forward the frontend
kubectl port-forward svc/frontend 3000:3000 -n donekaro

# Port-forward chat-api (for direct API testing)
kubectl port-forward svc/chat-api 8000:8000 -n donekaro
```

Open http://localhost:3000 in your browser.

---

## Option B: Docker Compose (Quick Local Dev)

For rapid development without Kubernetes overhead.

### 1. Create Local Secrets File

Create `secrets.json` in the project root (gitignored):

```json
{
  "postgres-credentials": {
    "connection-string": "host=YOUR_NEON_HOST port=5432 user=YOUR_USER password=YOUR_PASSWORD dbname=donekaro sslmode=require"
  },
  "gemini-credentials": {
    "api-key": "YOUR_GEMINI_API_KEY"
  },
  "vapid-credentials": {
    "public-key": "YOUR_VAPID_PUBLIC_KEY",
    "private-key": "YOUR_VAPID_PRIVATE_KEY",
    "mailto": "mailto:you@example.com"
  },
  "auth-credentials": {
    "jwt-secret": "YOUR_JWT_SECRET"
  }
}
```

### 2. Start All Services

```bash
docker compose up --build
```

This starts:
- **chat-api** on port 8000 (with Dapr sidecar on 3500)
- **notification-service** (with Dapr sidecar on 3501)
- **recurring-engine** (with Dapr sidecar on 3502)
- **frontend** on port 3000
- **Redpanda** (Kafka-compatible) on port 9092
- **Dapr placement service**

### 3. Access the Application

Open http://localhost:3000 in your browser.

---

## Option C: Dapr Multi-App Run (Development Mode)

For running services directly on your machine (no containers).

### 1. Install Dapr Standalone

```bash
dapr init
```

### 2. Install Python Dependencies (per service)

```bash
cd services/chat-api && pip install -r requirements.txt && cd ../..
cd services/notification-service && pip install -r requirements.txt && cd ../..
cd services/recurring-engine && pip install -r requirements.txt && cd ../..
```

### 3. Install Frontend Dependencies

```bash
cd frontend && npm install && cd ..
```

### 4. Run All Services with Dapr

```bash
dapr run -f dapr.yaml
```

The `dapr.yaml` multi-app run configuration starts all three services with their Dapr sidecars and local component configurations.

---

## Verifying the System

### 1. Health Check

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","service":"chat-api","dapr":{"connected":true,...}}
```

### 2. Send a Chat Message

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"message": "Create a task: Buy groceries"}'

# Expected: {"response":"Task 'Buy groceries' created successfully.","conversation_id":"...","task_action":{"action":"created",...}}
```

### 3. Verify Event Published

```bash
# Check Kafka topics (via Strimzi/Redpanda)
kubectl exec -it kafka-cluster-kafka-0 -n kafka -- \
  bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 \
  --topic task-events --from-beginning --max-messages 1
```

### 4. Test SSE Stream

```bash
curl -N http://localhost:8000/events/stream?userId=YOUR_USER_ID \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Accept: text/event-stream"

# In another terminal, create a task — you should see the SSE event
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Dapr sidecar not injecting | Ensure pod annotations: `dapr.io/enabled: "true"`, `dapr.io/app-id: "service-name"` |
| Kafka connection refused | Wait for Strimzi cluster to be Ready; check broker bootstrap address |
| State store 500 errors | Verify PostgreSQL connection string in Kubernetes secret |
| ETag 409 conflicts | Read the latest state before writing; include ETag in save request |
| Jobs API 404 | Ensure Dapr version >= 1.14; Jobs API is at `v1.0-alpha1` path |
| SSE not receiving events | Verify chat-api is subscribed to `task-updates` topic in Dapr subscriptions |

---

## Project Layout Reference

```
todo-phase-5/
├── services/
│   ├── chat-api/           → Port 8000 (Dapr: 3500)
│   ├── notification-service/ → No HTTP port (Dapr: 3501, event-driven)
│   └── recurring-engine/   → No HTTP port (Dapr: 3502, event + jobs)
├── frontend/               → Port 3000
├── dapr-components/
│   ├── local/              → Local dev Dapr configs
│   └── production/         → Production Dapr configs
├── k8s-manifests/          → Kubernetes resources
├── helm/                   → Helm chart for packaging
├── docker-compose.yaml     → Quick local dev
└── dapr.yaml               → Dapr multi-app run config
```
