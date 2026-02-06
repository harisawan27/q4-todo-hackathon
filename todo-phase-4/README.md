# GIAIC Phase 4: Cloud-Native AI Chatbot

A cloud-native deployment of the AI Chatbot application using Kubernetes (Minikube) and Helm.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                            │
│                                                                 │
│  ┌─────────────────┐       ┌─────────────────────────────────┐ │
│  │   Frontend      │       │         Backend                 │ │
│  │   (Next.js)     │──────▶│         (FastAPI)               │ │
│  │   Port: 3000    │       │         Port: 8001              │ │
│  │   NodePort:30080│       │         ClusterIP               │ │
│  └─────────────────┘       └─────────────────────────────────┘ │
│          │                              │                       │
│          │                              │                       │
│  ┌───────▼───────┐           ┌──────────▼──────────┐           │
│  │   ConfigMap   │           │      Secrets        │           │
│  │ (API URLs)    │           │ (API Keys, DB URL)  │           │
│  └───────────────┘           └─────────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │   External PostgreSQL  │
                         │   (Phase 2 Database)   │
                         └────────────────────────┘
```

## Components

| Component | Technology | Port | Service Type |
|-----------|------------|------|--------------|
| Frontend | Next.js 16, React 19 | 3000 | NodePort (30080) |
| Backend | Python 3.10, FastAPI | 8001 | ClusterIP |
| Database | PostgreSQL | 5432 | External |

## Quick Start

### Prerequisites

- Docker Desktop
- Minikube v1.32+
- kubectl v1.28+
- Helm v3.13+

### Deploy

```bash
# 1. Start Minikube
minikube start --memory=4096 --cpus=2

# 2. Configure Docker for Minikube
& minikube docker-env --shell powershell | Invoke-Expression  # Windows
eval $(minikube docker-env)  # Linux/macOS

# 3. Build images
docker build -t chatbot-backend:local ./backend
docker build -t chatbot-frontend:local ./frontend

# 4. Create secrets
kubectl create secret generic chatbot-secrets \
  --from-literal=GEMINI_API_KEY='your-key' \
  --from-literal=DATABASE_URL='postgresql://...'

# 5. Deploy with Helm
helm install chatbot ./charts/chatbot

# 6. Access the application
minikube service chatbot-frontend --url
```

See [quickstart.md](specs/001-cloud-native-chatbot/quickstart.md) for detailed instructions.

## Project Structure

```
todo-phase-4/
├── backend/                 # FastAPI backend service
│   ├── app/                # Application code
│   ├── Dockerfile          # Production container image
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend service
│   ├── src/               # Application code
│   ├── Dockerfile         # Production container image
│   └── package.json       # Node.js dependencies
├── charts/chatbot/        # Helm chart
│   ├── Chart.yaml         # Chart metadata
│   ├── values.yaml        # Configurable values
│   └── templates/         # Kubernetes manifests
├── k8s/                   # Raw K8s examples
│   └── secrets-example.yaml
├── docker-compose.yml     # Local development
└── specs/                 # Feature specifications
```

## Success Criteria

- [x] SC-001: Single `helm install` deployment
- [ ] SC-002: Pods running within 2 minutes
- [ ] SC-003: Chat functionality works
- [x] SC-004: Service-to-service via K8s DNS
- [ ] SC-005: Combined image < 500MB
- [x] SC-006: Stateless services
- [ ] SC-007: Rolling updates without downtime
- [x] SC-008: Credentials in Secrets only

## AI-Assisted Tools (Optional)

| Tool | Purpose |
|------|---------|
| Gordon | Docker AI for Dockerfile generation |
| kubectl-ai | Natural language K8s commands |
| Kagent | AI-powered cluster monitoring |

## License

GIAIC Phase 4 Educational Project
