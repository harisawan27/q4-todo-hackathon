#!/usr/bin/env bash
set -euo pipefail

echo "=== DoneKaro Local Deployment ==="
echo ""

# Use Minikube Docker daemon
echo "[1/4] Configuring Docker to use Minikube..."
eval $(minikube docker-env)

# Build Docker images
echo ""
echo "[2/4] Building Docker images..."
docker build -t donekaro/chat-api:local -f services/chat-api/Dockerfile services/chat-api/
docker build -t donekaro/notification-service:local -f services/notification-service/Dockerfile services/notification-service/
docker build -t donekaro/recurring-engine:local -f services/recurring-engine/Dockerfile services/recurring-engine/

if [ -d "frontend" ] && [ -f "frontend/Dockerfile" ]; then
    docker build -t donekaro/frontend:local -f frontend/Dockerfile frontend/
fi

echo "Docker images built successfully."

# Deploy with Helm
echo ""
echo "[3/4] Deploying with Helm..."
helm upgrade --install donekaro helm/donekaro \
    -f helm/donekaro/values-local.yaml \
    --namespace donekaro \
    --create-namespace \
    --wait --timeout 300s

# Verify deployment
echo ""
echo "[4/4] Verifying deployment..."
kubectl get pods -n donekaro
echo ""
echo "=== Deployment complete! ==="
echo ""
echo "Access the application:"
echo "  minikube service frontend -n donekaro --url"
echo ""
echo "Or port-forward:"
echo "  kubectl port-forward svc/chat-api 8000:80 -n donekaro"
echo "  kubectl port-forward svc/frontend 3000:80 -n donekaro"
