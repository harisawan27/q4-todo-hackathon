# Quickstart: Cloud-Native AI Chatbot Deployment

**Feature**: 001-cloud-native-chatbot
**Date**: 2026-02-02

This guide walks through deploying the AI Chatbot to a local Minikube Kubernetes cluster.

## Prerequisites

Ensure the following tools are installed:

| Tool | Version | Installation |
|------|---------|--------------|
| Docker Desktop | 24+ | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) |
| Minikube | 1.32+ | `winget install minikube` or [minikube.sigs.k8s.io](https://minikube.sigs.k8s.io/docs/start/) |
| kubectl | 1.28+ | Bundled with Docker Desktop or `winget install kubectl` |
| Helm | 3.13+ | `winget install Helm.Helm` or [helm.sh/docs/intro/install](https://helm.sh/docs/intro/install/) |

### Optional AI Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| Gordon | Dockerfile generation | Built into Docker Desktop |
| kubectl-ai | Natural language K8s commands | `go install github.com/sozercan/kubectl-ai@latest` |
| Kagent | AI cluster monitoring | Check official documentation |

## Step 1: Start Minikube

```bash
# Start Minikube with recommended resources
minikube start --memory=4096 --cpus=2 --driver=docker

# Verify cluster is running
kubectl cluster-info

# Enable Ingress addon (optional)
minikube addons enable ingress
```

## Step 2: Configure Docker Environment

Build images directly in Minikube's Docker daemon to avoid registry setup:

```bash
# On Windows PowerShell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# On Linux/macOS bash
eval $(minikube docker-env)

# Verify you're using Minikube's Docker
docker info | grep -i name
```

## Step 3: Build Container Images

```bash
# Navigate to project root
cd todo-phase-4

# Build backend image
docker build -t chatbot-backend:local ./backend

# Build frontend image
docker build -t chatbot-frontend:local ./frontend

# Verify images exist
docker images | grep chatbot
```

Expected output:
```
chatbot-frontend   local   abc123   1 minute ago   180MB
chatbot-backend    local   def456   2 minutes ago  280MB
```

## Step 4: Create Kubernetes Secrets

Create a file `secrets.env` (do NOT commit this file):

```env
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=postgresql://user:password@host:5432/database
```

Then create the Kubernetes Secret:

```bash
# Create secret from env file
kubectl create secret generic chatbot-secrets --from-env-file=secrets.env

# Or create from literal values
kubectl create secret generic chatbot-secrets \
  --from-literal=GEMINI_API_KEY='your-key' \
  --from-literal=DATABASE_URL='postgresql://...'

# Verify secret exists
kubectl get secrets chatbot-secrets
```

## Step 5: Deploy with Helm

```bash
# Validate the Helm chart
helm lint ./charts/chatbot

# Preview the generated manifests
helm template chatbot ./charts/chatbot

# Install the release
helm install chatbot ./charts/chatbot

# Watch pods start up
kubectl get pods -w
```

Wait until all pods show `Running` status (should be < 2 minutes).

## Step 6: Access the Application

### Option A: Minikube Service (Recommended)

```bash
# Get the frontend URL
minikube service chatbot-frontend --url

# Opens browser automatically
minikube service chatbot-frontend
```

### Option B: Port Forwarding

```bash
# Forward frontend to localhost:3000
kubectl port-forward svc/chatbot-frontend 3000:3000

# Access at http://localhost:3000
```

### Option C: Minikube Tunnel (for LoadBalancer services)

```bash
# In a separate terminal, run:
minikube tunnel

# Get external IP
kubectl get svc chatbot-frontend
```

## Step 7: Verify Deployment

### Check Pod Status

```bash
kubectl get pods
# Expected: 2 pods, both Running, 0 restarts

kubectl get services
# Expected: chatbot-frontend and chatbot-backend services
```

### Check Pod Logs

```bash
# Backend logs
kubectl logs -l app=chatbot-backend

# Frontend logs
kubectl logs -l app=chatbot-frontend
```

### Test Chat Functionality

1. Open the frontend URL in your browser
2. Send a test message: "Hello, can you help me?"
3. Verify you receive an AI response

### Health Check Verification

```bash
# Backend health
kubectl exec -it $(kubectl get pod -l app=chatbot-backend -o jsonpath='{.items[0].metadata.name}') -- curl localhost:8001/health

# Expected: {"status": "healthy"}
```

## Troubleshooting

### Pods Not Starting

```bash
# Describe pod for events
kubectl describe pod -l app=chatbot-backend

# Check if images exist
docker images | grep chatbot
```

### ImagePullBackOff Error

Ensure images were built in Minikube's Docker context:
```bash
& minikube docker-env --shell powershell | Invoke-Expression
docker images | grep chatbot
```

### Database Connection Failed

1. Verify DATABASE_URL in secret is correct
2. Ensure database is accessible from Minikube:
   ```bash
   # If database is on host machine
   minikube ssh "curl -v telnet://host.minikube.internal:5432"
   ```
3. Update DATABASE_URL to use `host.minikube.internal` instead of `localhost`

### Frontend Cannot Reach Backend

```bash
# Verify backend service exists
kubectl get svc chatbot-backend

# Test DNS resolution from frontend pod
kubectl exec -it $(kubectl get pod -l app=chatbot-frontend -o jsonpath='{.items[0].metadata.name}') -- nslookup chatbot-backend
```

## Cleanup

```bash
# Uninstall the Helm release
helm uninstall chatbot

# Delete the secret
kubectl delete secret chatbot-secrets

# Stop Minikube (preserves cluster)
minikube stop

# Delete Minikube cluster (full cleanup)
minikube delete
```

## Useful Commands

```bash
# View all resources
kubectl get all

# Restart a deployment
kubectl rollout restart deployment chatbot-backend

# Scale replicas
kubectl scale deployment chatbot-frontend --replicas=2

# View resource usage
kubectl top pods

# Interactive shell in pod
kubectl exec -it <pod-name> -- /bin/sh
```

## AI-Assisted Commands (Optional)

If kubectl-ai is installed:

```bash
# Natural language queries
kubectl-ai "show me all pods that are not running"
kubectl-ai "why is my backend pod failing"
kubectl-ai "show me the logs for the frontend"
```

---

**Success Criteria Checklist**:
- [ ] Helm install completes successfully
- [ ] Both pods reach Running status < 2 minutes
- [ ] Chat messages send and receive responses
- [ ] No secrets in plain text files
- [ ] Combined image size < 500MB
