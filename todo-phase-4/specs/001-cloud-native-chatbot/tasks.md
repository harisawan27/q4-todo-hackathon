# Tasks: Cloud-Native AI Chatbot Migration

**Input**: Design documents from `/specs/001-cloud-native-chatbot/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete)

**Tests**: Tests are NOT explicitly requested in the feature specification. Test tasks are omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/` - Python FastAPI server
- **Frontend**: `frontend/` - Next.js chat interface
- **Charts**: `charts/chatbot/` - Helm chart directory
- **Specs**: `specs/001-cloud-native-chatbot/` - Feature documentation

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure verification

- [X] T001 Verify backend source code exists in backend/app/main.py
- [X] T002 Verify frontend source code exists in frontend/src/app/page.tsx
- [X] T003 [P] Create charts/chatbot/ directory structure for Helm charts
- [X] T004 [P] Create charts/chatbot/templates/ directory for K8s manifests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core containerization that MUST be complete before ANY user story can be implemented

**Why Foundational**: Docker images are required for all Kubernetes deployments. Without container images, nothing can be deployed to Minikube.

- [X] T005 Generate backend/.dockerignore with exclusions for __pycache__, .env, .git, venv, .pytest_cache, .mypy_cache
- [X] T006 Generate backend/Dockerfile with multi-stage build for Python FastAPI (base python:3.10-slim, non-root user, port 8001, health check)
- [ ] T007 Verify backend Dockerfile builds successfully with `docker build -t chatbot-backend:local ./backend`
- [X] T008 [P] Generate frontend/.dockerignore with exclusions for node_modules, .next, .git, .env.local, .env
- [X] T009 [P] Generate frontend/Dockerfile with 3-stage build for Next.js 16 (node:18-alpine, non-root user, port 3000, standalone output)
- [ ] T010 Verify frontend Dockerfile builds successfully with `docker build -t chatbot-frontend:local ./frontend`
- [X] T011 Create docker-compose.yml at repo root for local multi-container integration testing
- [ ] T012 Verify combined Docker image size is under 500MB (chatbot-backend + chatbot-frontend)

**Checkpoint**: Foundation ready - container images built and verified. User story implementation can now begin.

---

## Phase 3: User Story 2 - Containerize Services Using Gordon (Priority: P1)

**Goal**: Generate optimized Dockerfiles using Gordon (Docker AI) or fallback to direct generation

**Independent Test**: Build Docker images and run them locally in standalone containers to verify they work

**Why P1**: Containerization is a prerequisite for Kubernetes deployment. Without properly built container images, nothing can be deployed.

### Implementation for User Story 2

- [X] T013 [US2] Document Gordon CLI usage for backend Dockerfile generation in specs/001-cloud-native-chatbot/quickstart.md
- [X] T014 [US2] Document Gordon CLI usage for frontend Dockerfile generation in specs/001-cloud-native-chatbot/quickstart.md
- [ ] T015 [US2] Test backend container locally: `docker run -p 8001:8001 --env-file backend/.env.example chatbot-backend:local`
- [ ] T016 [US2] Verify backend health endpoint responds: `curl http://localhost:8001/health`
- [ ] T017 [US2] Test frontend container locally: `docker run -p 3000:3000 chatbot-frontend:local`
- [ ] T018 [US2] Verify frontend UI loads in browser at http://localhost:3000
- [ ] T019 [US2] Test full stack locally with docker-compose up and verify chat flow

**Checkpoint**: User Story 2 complete - both services containerized and verified locally

---

## Phase 4: User Story 3 - Create Helm Charts for Deployment (Priority: P1)

**Goal**: Create Helm charts defining complete Kubernetes deployment configuration

**Independent Test**: Run `helm lint` and `helm template` to validate chart, then install to Minikube

**Why P1**: Helm charts provide declarative configuration needed for consistent, repeatable deployments

### Implementation for User Story 3

- [X] T020 [P] [US3] Create charts/chatbot/Chart.yaml with name=chatbot, version=0.1.0, appVersion=1.0.0
- [X] T021 [P] [US3] Create charts/chatbot/templates/_helpers.tpl with common label templates
- [X] T022 [US3] Create charts/chatbot/values.yaml with configurable parameters for both services
- [X] T023 [P] [US3] Create charts/chatbot/templates/backend-deployment.yaml with Deployment spec (replicas, image, env from secrets/configmap, probes, resources)
- [X] T024 [P] [US3] Create charts/chatbot/templates/backend-service.yaml with ClusterIP Service spec (port 8001)
- [X] T025 [P] [US3] Create charts/chatbot/templates/frontend-deployment.yaml with Deployment spec (replicas, image, env from configmap, probes, resources)
- [X] T026 [P] [US3] Create charts/chatbot/templates/frontend-service.yaml with NodePort Service spec (port 3000)
- [X] T027 [US3] Create charts/chatbot/templates/configmap.yaml with non-sensitive config (NEXT_PUBLIC_API_URL, LLM_MODEL)
- [X] T028 [US3] Create charts/chatbot/templates/secrets.yaml with placeholder template for GEMINI_API_KEY, DATABASE_URL
- [ ] T029 [US3] Validate Helm chart with `helm lint ./charts/chatbot`
- [ ] T030 [US3] Generate YAML output with `helm template chatbot ./charts/chatbot` and verify validity

**Checkpoint**: User Story 3 complete - Helm chart created and validated

---

## Phase 5: User Story 6 - Configure Environment Variables Securely (Priority: P1)

**Goal**: Configure sensitive environment variables using Kubernetes Secrets and ConfigMaps

**Independent Test**: Create Secrets/ConfigMaps and verify backend pod can access required credentials

**Why P1**: Secure credential management is essential for the backend to connect to LLM API and database

### Implementation for User Story 6

- [X] T031 [US6] Document Secret creation command in specs/001-cloud-native-chatbot/quickstart.md
- [X] T032 [US6] Create k8s/secrets-example.yaml template showing Secret structure (without actual values)
- [X] T033 [US6] Update charts/chatbot/values.yaml with secretRef configuration for backend deployment
- [X] T034 [US6] Update charts/chatbot/templates/backend-deployment.yaml to mount secrets as environment variables
- [X] T035 [US6] Update charts/chatbot/templates/frontend-deployment.yaml to read NEXT_PUBLIC_API_URL from ConfigMap

**Checkpoint**: User Story 6 complete - environment variables configured securely via Secrets and ConfigMaps

---

## Phase 6: User Story 1 - Deploy Chatbot to Local Kubernetes Cluster (Priority: P1) MVP

**Goal**: Complete chatbot application running on local Minikube cluster with both services communicating

**Independent Test**: Deploy Helm chart and verify chatbot UI is accessible and can communicate with backend

**Why MVP**: This is the core deliverable - a working cloud-native deployment is the foundation for all other features

### Implementation for User Story 1

- [ ] T036 [US1] Document Minikube startup command in specs/001-cloud-native-chatbot/quickstart.md: `minikube start --memory=4096 --cpus=2`
- [ ] T037 [US1] Document Minikube Docker env configuration in specs/001-cloud-native-chatbot/quickstart.md
- [ ] T038 [US1] Rebuild Docker images inside Minikube Docker daemon (eval $(minikube docker-env) then build)
- [ ] T039 [US1] Create Kubernetes Secret with actual API keys: `kubectl create secret generic chatbot-secrets --from-literal=GEMINI_API_KEY=... --from-literal=DATABASE_URL=...`
- [ ] T040 [US1] Deploy application with `helm install chatbot ./charts/chatbot`
- [ ] T041 [US1] Verify both pods reach Running status within 2 minutes: `kubectl get pods -w`
- [ ] T042 [US1] Verify pod logs show no errors: `kubectl logs -l app.kubernetes.io/name=chatbot`
- [ ] T043 [US1] Get frontend URL and access in browser: `minikube service chatbot-frontend --url`
- [ ] T044 [US1] Send test chat message and verify AI response received within 5 seconds
- [ ] T045 [US1] Verify no pod restarts after 5 minutes: `kubectl get pods`

**Checkpoint**: User Story 1 (MVP) complete - chatbot deployed and functional on Minikube

---

## Phase 7: User Story 4 - Manage Cluster Using kubectl-ai (Priority: P2)

**Goal**: Use kubectl-ai for natural language Kubernetes cluster management

**Independent Test**: Run kubectl-ai commands to query pod status, view logs, and describe resources

**Why P2**: Enhances developer experience but not essential for core functionality

### Implementation for User Story 4

- [X] T046 [P] [US4] Document kubectl-ai installation in specs/001-cloud-native-chatbot/quickstart.md
- [X] T047 [P] [US4] Document kubectl-ai example prompts in specs/001-cloud-native-chatbot/quickstart.md (show pods, describe deployment, get logs)
- [ ] T048 [US4] Test kubectl-ai: "show me all chatbot pods" and verify correct kubectl translation
- [ ] T049 [US4] Test kubectl-ai: "what's the status of the backend deployment" and verify diagnostic output

**Checkpoint**: User Story 4 complete - kubectl-ai documented and verified

---

## Phase 8: User Story 5 - Monitor Cluster Health Using Kagent (Priority: P2)

**Goal**: Use Kagent for AI-powered cluster monitoring and health insights

**Independent Test**: Run Kagent health checks and observe cluster status reports

**Why P2**: Monitoring enhances operational visibility but core chatbot functions without it

### Implementation for User Story 5

- [X] T050 [P] [US5] Document Kagent installation in specs/001-cloud-native-chatbot/quickstart.md
- [X] T051 [P] [US5] Document Kagent usage examples in specs/001-cloud-native-chatbot/quickstart.md
- [ ] T052 [US5] Test Kagent cluster health query and verify node/pod status report
- [ ] T053 [US5] Test Kagent service health query for chatbot frontend and backend

**Checkpoint**: User Story 5 complete - Kagent documented and verified

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation completion and final verification

- [X] T054 [P] Update specs/001-cloud-native-chatbot/quickstart.md with complete deployment workflow
- [X] T055 [P] Create README.md section documenting the cloud-native architecture
- [ ] T056 Verify all 8 success criteria (SC-001 to SC-008) are met
- [ ] T057 Test rolling update: change image tag and run `helm upgrade chatbot ./charts/chatbot`
- [ ] T058 Verify rolling update completes without service downtime

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories (Docker images required)
- **User Story 2 (Phase 3)**: Depends on Foundational - containerization verification
- **User Story 3 (Phase 4)**: Depends on Foundational - requires images for Helm chart
- **User Story 6 (Phase 5)**: Depends on User Story 3 - requires Helm chart to configure
- **User Story 1 (Phase 6)**: Depends on US2, US3, US6 - requires all P1 stories complete for MVP deployment
- **User Story 4 (Phase 7)**: Can start after US1 (cluster must be deployed)
- **User Story 5 (Phase 8)**: Can start after US1 (cluster must be deployed)
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Depends On | Can Start After |
|-------|----------|------------|-----------------|
| US2 (Containerize) | P1 | Foundational | Phase 2 complete |
| US3 (Helm Charts) | P1 | Foundational | Phase 2 complete |
| US6 (Secrets) | P1 | US3 | Phase 4 complete |
| US1 (Deploy) | P1 | US2, US3, US6 | Phase 5 complete |
| US4 (kubectl-ai) | P2 | US1 | Phase 6 complete |
| US5 (Kagent) | P2 | US1 | Phase 6 complete |

### Within Each User Story

- Infrastructure before services
- Configuration before deployment
- Core implementation before verification
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 2 Parallel Tasks**:
- T005 (backend .dockerignore) || T008 (frontend .dockerignore)
- T006 (backend Dockerfile) || T009 (frontend Dockerfile)

**Phase 4 Parallel Tasks** (Helm Chart Generation):
- T020 (Chart.yaml) || T021 (_helpers.tpl)
- T023 (backend-deployment) || T024 (backend-service) || T025 (frontend-deployment) || T026 (frontend-service)

**Phase 7/8 Parallel**:
- User Story 4 and User Story 5 can proceed in parallel (both P2, independent)

---

## Parallel Example: Helm Chart Templates

```bash
# Launch all independent template files together:
Task: "Create charts/chatbot/templates/backend-deployment.yaml"
Task: "Create charts/chatbot/templates/backend-service.yaml"
Task: "Create charts/chatbot/templates/frontend-deployment.yaml"
Task: "Create charts/chatbot/templates/frontend-service.yaml"

# Then sequential (depends on above):
Task: "Validate Helm chart with helm lint"
```

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3, 6 - All P1)

1. Complete Phase 1: Setup (verify source code)
2. Complete Phase 2: Foundational (build Docker images)
3. Complete Phase 3: User Story 2 (verify containerization)
4. Complete Phase 4: User Story 3 (create Helm charts)
5. Complete Phase 5: User Story 6 (configure secrets)
6. Complete Phase 6: User Story 1 (deploy to Minikube)
7. **STOP and VALIDATE**: Test chatbot end-to-end
8. Deploy/demo if ready (MVP complete!)

### Incremental Delivery

1. Foundation ready (Docker images built)
2. Add Helm charts (deployment configuration ready)
3. Add secrets configuration (security ready)
4. Deploy MVP (US1 complete - working chatbot on K8s)
5. Add kubectl-ai (US4 - enhanced cluster management)
6. Add Kagent (US5 - enhanced monitoring)
7. Polish and document

### Success Criteria Verification

| Criteria | Task | Verification |
|----------|------|--------------|
| SC-001 | T040 | `helm install` completes successfully |
| SC-002 | T041 | Both pods Running within 2 minutes |
| SC-003 | T044 | Chat message receives AI response |
| SC-004 | T027, T035 | Frontend uses internal DNS |
| SC-005 | T012 | Combined image size < 500MB |
| SC-006 | T045 | No restarts, stateless services |
| SC-007 | T057 | Rolling update without downtime |
| SC-008 | T039 | Credentials in Secrets only |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Gordon/kubectl-ai/Kagent are optional - fallback to direct generation if unavailable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
