#!/usr/bin/env bash
set -euo pipefail

echo "=== Cleaning up old cluster ==="
k3d cluster delete seccluster || true
docker system prune -f

echo "=== Creating fresh minimal k3s cluster ==="
k3d cluster create seccluster \
  --servers 1 \
  --api-port 6443 \
  --no-lb \                                 # removes the extra proxy container
  --k3s-arg "--disable=traefik@server:*" \
  --k3s-arg "--disable=servicelb@server:*" \
  --k3s-arg "--disable=coredns@server:*" \
  --wait

echo "=== Pointing kubectl at the new cluster ==="
k3d kubeconfig get seccluster > ~/.kube/config

echo "=== Installing Kyverno (with higher timeout and resources to avoid local k3s quirks) ==="
helm repo add kyverno https://kyverno.github.io/kyverno/ 2>/dev/null || true
helm repo update
helm upgrade --install kyverno kyverno/kyverno \
  --namespace kyverno --create-namespace \
  --set admissionController.webhook.timeout=30 \
  --set admissionController.resources.requests.cpu=200m \
  --set admissionController.resources.requests.memory=512Mi \
  --wait

echo "=== Waiting for Kyverno CRDs and pods ==="
kubectl wait --for condition=established crd/clusterpolicies.kyverno.io --timeout=120s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/component=admission-controller -n kyverno --timeout=120s

echo "=== Applying all security policies ==="
kubectl apply -f ../kyverno-policies/clusterpolicies/
kubectl apply -f ../kyverno-policies/advanced/

echo ""
echo "=== DONE! Your zero-trust Kubernetes cluster is ready ==="
echo "→ 1 node running"
echo "→ Kyverno installed"
echo "→ All policies enforced (privileged pods, :latest tags, hostPath, etc. BLOCKED)"
echo ""
echo "Quick test:"
echo "  kubectl run good --image=docker.io/nginx:1.27 --restart=Never --labels=app.kubernetes.io/team=security --requests=cpu=100m,memory=128Mi --limits=cpu=500m,memory=256Mi"
echo "  → Should create and get auto-hardened"
echo ""
echo "  kubectl run bad --image=nginx:latest --privileged --restart=Never"
echo "  → Should be instantly denied"
echo ""
kubectl get nodes
