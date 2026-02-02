<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.1.0 (MINOR - Added Source Code Analysis section)
Modified principles: None
Added sections:
  - Source Code Analysis (ports, dependencies, communication patterns)
  - Project Tasks section (Task 1 & Task 2 scope)
Removed sections: None
Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Reviewed (No changes needed)
  - .specify/templates/spec-template.md: ✅ Reviewed (No changes needed)
  - .specify/templates/tasks-template.md: ✅ Reviewed (No changes needed)
Follow-up TODOs: None
-->

# Cloud-Native Todo Chatbot Constitution

## Core Principles

### I. Spec-Driven Development (SDD)

All features MUST follow the SDD workflow: `spec.md` → `plan.md` → `tasks.md` → implementation.
No implementation work begins without an approved specification. Specifications define acceptance
criteria, and plans define architecture decisions before any code is generated.

**Rationale**: Ensures traceability, reduces rework, and maintains alignment between requirements
and implementation throughout the containerization and deployment process.

### II. Zero Manual Coding

The Agentic DevOps Engineer (Claude) MUST generate ALL files, scripts, configurations, Dockerfiles,
Kubernetes manifests, and Helm charts. The student operator MUST NOT write or edit code manually.
All changes flow through the AI agent using specified tooling.

**Rationale**: This is a learning exercise in agentic automation. Manual intervention defeats the
educational purpose and breaks reproducibility guarantees.

### III. Containerization-First

Both frontend and backend components MUST be containerized using Docker before any deployment
considerations. Use 'Gordon' (Docker AI) instructions for generating optimized Dockerfiles.
Containers MUST:
- Use multi-stage builds to minimize image size
- Run as non-root users for security
- Include health check endpoints
- Follow the principle of one process per container

**Rationale**: Containers provide consistent environments from development to production and are
prerequisites for Kubernetes deployment.

### IV. Kubernetes-Native Deployment

All deployments target Minikube (local Kubernetes cluster). Use 'kubectl-ai' or 'Kagent' for
generating Kubernetes manifests and Helm charts. Manifests MUST include:
- Deployment resources with proper resource limits
- Service resources for internal/external networking
- ConfigMaps for non-sensitive configuration
- Secrets for sensitive data (database URLs, API keys)
- Health probes (liveness and readiness)

**Rationale**: Kubernetes provides declarative infrastructure, self-healing, and scalability
patterns essential for cloud-native applications.

### V. Environment Parity

Development, staging, and production environments MUST maintain parity. Configuration differences
MUST be externalized through environment variables, ConfigMaps, or Secrets. Application images
MUST be identical across environments—only configuration changes.

**Rationale**: Prevents "works on my machine" issues and ensures reliable deployments across
the development lifecycle.

### VI. Observability & Debuggability

All services MUST expose:
- Health check endpoints (`/health` or `/healthz`)
- Structured JSON logging to stdout/stderr
- Metrics endpoints where applicable (e.g., `/metrics` for Prometheus)

Kubernetes deployments MUST configure appropriate liveness and readiness probes.

**Rationale**: Observable systems are debuggable systems. Cloud-native applications require
standardized telemetry for operational management.

## Source Code Analysis

Analysis completed from `../todo-phase-3` source code, now copied to `frontend/` and `backend/`.

### Port Configuration

| Service | Port | Protocol | Notes |
|---------|------|----------|-------|
| Backend (FastAPI) | 8001 | HTTP | uvicorn server, API endpoints |
| Frontend (Next.js) | 3000 | HTTP | Development server, SSR |
| PostgreSQL | 5432 | TCP | External database (shared with Phase 2) |

### Backend Dependencies

**Python 3.10+ with requirements.txt:**
- `fastapi>=0.109.0` - Web framework
- `uvicorn[standard]>=0.27.0` - ASGI server
- `sqlmodel>=0.0.16` - ORM (SQLAlchemy + Pydantic)
- `psycopg2-binary>=2.9.9` - PostgreSQL driver
- `python-dotenv>=1.0.0` - Environment configuration
- `pydantic-settings>=2.1.0` - Settings management
- `litellm>=1.30.0` - Multi-provider LLM support
- `google-generativeai>=0.5.0` - Gemini API
- `openai>=1.12.0` - OpenAI API (fallback)
- `mcp>=1.0.0` - Model Context Protocol SDK
- `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, `httpx>=0.26.0` - Testing

### Frontend Dependencies

**Node.js 18+ with package.json:**
- `next@16.1.4` - React framework (App Router)
- `react@19.2.3`, `react-dom@19.2.3` - UI library
- `lucide-react@^0.563.0` - Icons
- `tailwindcss@^4` - CSS framework
- `typescript@^5` - Type safety

### Frontend-Backend Communication

| Aspect | Detail |
|--------|--------|
| Protocol | HTTP REST API |
| Base URL | `NEXT_PUBLIC_API_URL` (default: `http://localhost:8001`) |
| Primary Endpoint | `POST /api/{user_id}/chat` |
| Request Format | JSON: `{ message: string, conversation_id?: string }` |
| Response Format | JSON: `{ response: string, conversation_id: string }` |
| CORS | Configured for `http://localhost:3000` |
| Authentication | User ID passed in URL path (testing mode) |

### Environment Variables

**Backend (.env):**
- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini API key (primary)
- `OPENAI_API_KEY` - OpenAI API key (optional fallback)
- `LLM_MODEL` - Model selection (default: `gemini/gemini-2.5-flash`)

**Frontend (.env.local):**
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_USER_ID` - User ID for testing

### Existing Health Endpoint

Backend already exposes `GET /health` returning `{"status": "healthy"}` - ready for K8s probes.

## Technology Stack

**Source Application**: Todo AI Chatbot from `../todo-phase-3`

| Component | Technology | Notes |
|-----------|------------|-------|
| Frontend | Next.js 16.1.4 | TypeScript, React 19, Tailwind CSS v4 |
| Backend | Python 3.10+ FastAPI | LiteLLM integration, PostgreSQL via SQLModel |
| Database | PostgreSQL | Shared with Phase 2 (external to cluster) |
| Container Runtime | Docker | Multi-stage builds, Gordon AI assistance |
| Orchestration | Kubernetes (Minikube) | kubectl-ai/Kagent for manifest generation |
| Package Manager | Helm (optional) | For templated deployments |

## Project Tasks

### Task 1: Initialization & Analysis (COMPLETED)

1. ✅ Created `frontend/` and `backend/` directories within `todo-phase-4`
2. ✅ Copied relevant chatbot source code from `../todo-phase-3`
3. ✅ Analyzed code to identify:
   - Ports: Backend 8001, Frontend 3000, PostgreSQL 5432
   - Dependencies: See sections above
   - Communication: REST API via `POST /api/{user_id}/chat`

### Task 2: Specification Generation (PENDING)

- Draft `specs/containerization/spec.md` outlining:
  - Containerization strategy for frontend and backend
  - Kubernetes deployment requirements
  - Service networking within Minikube

## Development Workflow

### Standard SDD Cycle

1. **Specify** (`/sp.specify`): Create feature specification with acceptance criteria
2. **Plan** (`/sp.plan`): Generate implementation plan with architecture decisions
3. **Tasks** (`/sp.tasks`): Break plan into executable, dependency-ordered tasks
4. **Implement** (`/sp.implement`): Execute tasks using AI-generated code/configs
5. **Validate**: Verify against acceptance criteria
6. **Commit** (`/sp.git.commit_pr`): Commit changes with proper documentation

### Tooling Requirements

- **Containerization**: Gordon (Docker AI) for Dockerfile generation
- **Kubernetes**: kubectl-ai or Kagent for manifest/Helm chart generation
- **Local Cluster**: Minikube for deployment target
- **Version Control**: Git with conventional commits

### Quality Gates

- [ ] Specification approved before planning
- [ ] Plan approved before task generation
- [ ] Docker images build successfully
- [ ] Containers pass health checks locally
- [ ] Kubernetes manifests validate (`kubectl apply --dry-run`)
- [ ] Pods reach Running state in Minikube
- [ ] Services accessible via Minikube tunnel or NodePort

## Governance

This constitution supersedes all other development practices for the Phase 4 project. Amendments
require:
1. Documented rationale for the change
2. Impact analysis on existing artifacts
3. Version increment following semantic versioning:
   - MAJOR: Principle removal or fundamental redefinition
   - MINOR: New principle or significant expansion
   - PATCH: Clarifications and non-semantic refinements

All specifications, plans, and tasks MUST reference this constitution for compliance verification.
The Agentic DevOps Engineer MUST refuse to proceed if actions violate constitutional principles.

**Version**: 1.1.0 | **Ratified**: 2025-02-02 | **Last Amended**: 2025-02-02
