#!/usr/bin/env bash
set -euo pipefail

echo "=== DoneKaro Local Setup ==="
echo "Setting up Minikube + Dapr + Strimzi for local development"
echo ""

# Step 1: Check prerequisites
echo "[1/6] Checking prerequisites..."
command -v minikube >/dev/null 2>&1 || { echo "ERROR: minikube is required. Install from https://minikube.sigs.k8s.io/"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl is required. Install from https://kubernetes.io/docs/tasks/tools/"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "ERROR: helm is required. Install from https://helm.sh/docs/intro/install/"; exit 1; }
command -v dapr >/dev/null 2>&1 || { echo "ERROR: dapr CLI is required. Install from https://docs.dapr.io/getting-started/install-dapr-cli/"; exit 1; }
echo "All prerequisites found."

# Step 2: Start Minikube
echo ""
echo "[2/6] Starting Minikube..."
if minikube status | grep -q "Running"; then
    echo "Minikube already running."
else
    minikube start --cpus=4 --memory=8192 --driver=docker
fi

# Step 3: Initialize Dapr
echo ""
echo "[3/6] Initializing Dapr on Kubernetes..."
dapr init -k --wait || echo "Dapr may already be initialized."
echo "Dapr initialized. Verifying..."
dapr status -k

# Step 4: Install Strimzi Kafka Operator
echo ""
echo "[4/6] Installing Strimzi Kafka operator..."
kubectl create namespace donekaro --dry-run=client -o yaml | kubectl apply -f -
helm repo add strimzi https://strimzi.io/charts/ 2>/dev/null || true
helm repo update
helm upgrade --install strimzi-kafka-operator strimzi/strimzi-kafka-operator \
    --namespace donekaro \
    --wait --timeout 300s

# Step 5: Apply Kafka cluster and topics
echo ""
echo "[5/6] Deploying Kafka cluster and topics..."
kubectl apply -f k8s-manifests/base/infrastructure/kafka/kafka-cluster.yaml
echo "Waiting for Kafka cluster to be ready (this may take a few minutes)..."
kubectl wait kafka/donekaro-kafka --for=condition=Ready --timeout=600s -n donekaro || echo "Kafka may still be starting..."
kubectl apply -f k8s-manifests/base/infrastructure/kafka/kafka-topics.yaml

# Step 6: Apply secrets template
echo ""
echo "[6/6] Applying secrets template..."
echo "WARNING: Update the secrets in k8s-manifests/base/infrastructure/secrets/secrets-template.yaml before production use!"
kubectl apply -f k8s-manifests/base/infrastructure/secrets/secrets-template.yaml

echo ""
echo "=== Local setup complete! ==="
echo "Next: Run 'scripts/deploy-local.sh' to build and deploy services"
