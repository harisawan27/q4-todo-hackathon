#!/usr/bin/env bash
set -euo pipefail

echo "=== DoneKaro Production Deployment ==="
echo ""

# Validate environment
REGISTRY="${ACR_REGISTRY:?ERROR: Set ACR_REGISTRY environment variable (e.g., your-acr.azurecr.io)}"
TAG="${IMAGE_TAG:-latest}"

echo "Registry: ${REGISTRY}"
echo "Tag: ${TAG}"
echo ""

# Build and push images
echo "[1/3] Building and pushing Docker images..."
for SERVICE in chat-api notification-service recurring-engine; do
    echo "  Building ${SERVICE}..."
    docker build -t "${REGISTRY}/donekaro/${SERVICE}:${TAG}" -f "services/${SERVICE}/Dockerfile" "services/${SERVICE}/"
    docker push "${REGISTRY}/donekaro/${SERVICE}:${TAG}"
done

if [ -d "frontend" ] && [ -f "frontend/Dockerfile" ]; then
    echo "  Building frontend..."
    docker build -t "${REGISTRY}/donekaro/frontend:${TAG}" -f frontend/Dockerfile frontend/
    docker push "${REGISTRY}/donekaro/frontend:${TAG}"
fi

echo "Images pushed to ${REGISTRY}."

# Deploy with Helm
echo ""
echo "[2/3] Deploying with Helm (production values)..."
helm upgrade --install donekaro helm/donekaro \
    -f helm/donekaro/values-production.yaml \
    --set chatApi.image.repository="${REGISTRY}/donekaro/chat-api" \
    --set chatApi.image.tag="${TAG}" \
    --set notificationService.image.repository="${REGISTRY}/donekaro/notification-service" \
    --set notificationService.image.tag="${TAG}" \
    --set recurringEngine.image.repository="${REGISTRY}/donekaro/recurring-engine" \
    --set recurringEngine.image.tag="${TAG}" \
    --set frontend.image.repository="${REGISTRY}/donekaro/frontend" \
    --set frontend.image.tag="${TAG}" \
    --namespace donekaro \
    --create-namespace \
    --wait --timeout 600s

# Verify
echo ""
echo "[3/3] Verifying production deployment..."
kubectl get pods -n donekaro
kubectl get svc -n donekaro
kubectl get ingress -n donekaro
echo ""
echo "=== Production deployment complete! ==="
