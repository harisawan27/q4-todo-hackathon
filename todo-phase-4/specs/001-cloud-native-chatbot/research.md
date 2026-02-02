# Research: Cloud-Native AI Chatbot Migration

**Feature**: 001-cloud-native-chatbot
**Date**: 2026-02-02
**Status**: Complete

## Research Areas

### 1. Gordon (Docker AI) Integration

**Decision**: Use Gordon CLI for Dockerfile generation assistance

**Rationale**:
- Gordon is Docker's built-in AI assistant for container development
- Provides context-aware Dockerfile generation based on project analysis
- Supports multi-stage build optimization recommendations
- Integrates with Docker Desktop naturally

**Alternatives Considered**:
- Manual Dockerfile writing: Rejected (violates Zero Manual Coding principle)
- GitHub Copilot for Dockerfiles: Valid but Gordon is Docker-native
- Dockerfile generators (e.g., dfimage): Less intelligent, static templates

**Usage Pattern**:
```bash
# In Docker Desktop or via CLI
docker ai "Generate a Dockerfile for this Python FastAPI project"

# Or using Gordon directly
gordon ask "Create a multi-stage Dockerfile for Node.js 18 Next.js app"
```

**Fallback**: If Gordon is unavailable, the AI agent (Claude) will generate Dockerfiles using Docker best practices documented in the official Docker documentation.

---

### 2. kubectl-ai Integration

**Decision**: Use kubectl-ai for natural language Kubernetes management

**Rationale**:
- Translates natural language to kubectl commands
- Reduces syntax errors and learning curve
- Supports complex queries and troubleshooting
- Open-source with active community

**Alternatives Considered**:
- Raw kubectl commands: Valid but less intuitive for beginners
- K9s TUI: Visual but not AI-assisted
- Lens IDE: Good but heavyweight for learning

**Installation**:
```bash
# Install via Homebrew (macOS/Linux) or download binary
brew install kubectl-ai

# Or using Go
go install github.com/sozercan/kubectl-ai@latest
```

**Usage Pattern**:
```bash
# Natural language queries
kubectl-ai "show me all pods that are not running"
kubectl-ai "what's wrong with my deployment chatbot-backend"
kubectl-ai "scale the frontend to 3 replicas"
```

**Fallback**: If kubectl-ai is unavailable, the AI agent will provide standard kubectl commands for manual execution.

---

### 3. Kagent Integration

**Decision**: Use Kagent for AI-powered cluster monitoring and Helm chart generation

**Rationale**:
- Specialized for Kubernetes operational tasks
- Can generate Helm charts from natural language descriptions
- Provides cluster health insights
- Supports remediation suggestions

**Alternatives Considered**:
- Helm CLI only: Valid but less intelligent
- Kompose (Docker Compose to K8s): Limited to conversion only
- Kubernetes Dashboard: Visual but not AI-assisted

**Installation**:
```bash
# Install Kagent (check official docs for latest)
pip install kagent
# or
brew install kagent
```

**Usage Pattern**:
```bash
# Generate Helm chart
kagent create helm-chart "Create a Helm chart for a frontend and backend microservice"

# Cluster health
kagent diagnose "Why is my pod crashlooping?"
```

**Fallback**: If Kagent is unavailable, the AI agent will generate Helm charts directly using Helm best practices.

---

### 4. Minikube Configuration

**Decision**: Use Minikube with 4GB RAM, 2 CPUs for local Kubernetes

**Rationale**:
- Sufficient resources for 2 services + system pods
- Works within typical developer laptop constraints
- Supports LoadBalancer via `minikube tunnel`
- Built-in Docker daemon access

**Configuration**:
```bash
# Start Minikube with recommended resources
minikube start --memory=4096 --cpus=2 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server

# Configure Docker to build inside Minikube
eval $(minikube docker-env)
```

**Image Handling**:
- Build images inside Minikube's Docker daemon (no registry needed)
- Use `imagePullPolicy: Never` in deployments
- Or use `minikube image load <image>` for pre-built images

---

### 5. Service-to-Service Communication

**Decision**: Use Kubernetes internal DNS for service discovery

**Rationale**:
- No external network calls needed
- Automatic DNS resolution: `<service-name>.<namespace>.svc.cluster.local`
- Simplified configuration
- Works with ClusterIP services

**Configuration**:
- Frontend `NEXT_PUBLIC_API_URL`: `http://chatbot-backend:8001`
- Services use ClusterIP type (default)
- Ingress/NodePort only for external access to frontend

**Pattern**:
```yaml
# Frontend deployment env
env:
  - name: NEXT_PUBLIC_API_URL
    valueFrom:
      configMapKeyRef:
        name: chatbot-config
        key: backend-url
```

---

### 6. Secret Management

**Decision**: Use Kubernetes Secrets with manual creation

**Rationale**:
- Simple for local development
- No external secret manager needed
- Secrets encrypted at rest in etcd
- Standard Kubernetes pattern

**Alternatives Considered**:
- HashiCorp Vault: Overkill for local dev
- Sealed Secrets: Adds complexity
- External Secrets Operator: Needs external provider

**Pattern**:
```bash
# Create secrets from literal values
kubectl create secret generic chatbot-secrets \
  --from-literal=GEMINI_API_KEY='sk-...' \
  --from-literal=DATABASE_URL='postgresql://user:pass@host/db'

# Or from env file
kubectl create secret generic chatbot-secrets --from-env-file=.env.secrets
```

---

### 7. Health Check Endpoints

**Decision**: Use existing `/health` endpoint for backend, root `/` for frontend

**Rationale**:
- Backend already exposes `GET /health` returning `{"status": "healthy"}`
- Next.js serves root page as health indicator
- No code changes required

**Probe Configuration**:
```yaml
# Backend probes
livenessProbe:
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8001
  initialDelaySeconds: 10
  periodSeconds: 5

# Frontend probes
livenessProbe:
  httpGet:
    path: /
    port: 3000
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

### 8. Docker Multi-Stage Build Strategy

**Decision**: 3-stage build for frontend, 2-stage for backend

**Rationale**:
- Minimizes final image size
- Separates build dependencies from runtime
- Improves security (no build tools in production)

**Frontend Stages**:
1. `deps`: Install node_modules
2. `builder`: Build Next.js production output
3. `runner`: Copy only production artifacts

**Backend Stages**:
1. `builder`: Install Python dependencies
2. `runner`: Copy only runtime files

**Target Sizes**:
- Frontend: < 200MB (Alpine-based, standalone mode)
- Backend: < 300MB (Python slim, no dev dependencies)
- Combined: < 500MB (per SC-005)

---

## Resolved Clarifications

| Item | Resolution |
|------|------------|
| Gordon availability | Primary tool; Claude generates fallback if unavailable |
| kubectl-ai installation | Optional enhancement; standard kubectl as fallback |
| Kagent installation | Optional enhancement; direct Helm generation as fallback |
| Database connectivity | Use Minikube tunnel or configure host network |
| Image registry | Build inside Minikube, no registry needed |
| Ingress vs NodePort | NodePort for simplicity; Ingress optional |

---

## References

- [Docker Gordon AI](https://docs.docker.com/ai/)
- [kubectl-ai GitHub](https://github.com/sozercan/kubectl-ai)
- [Minikube Documentation](https://minikube.sigs.k8s.io/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
