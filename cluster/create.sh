#!/usr/bin/env bash
set -euo pipefail

k3d cluster delete seccluster || true
docker system prune -f

k3d cluster create seccluster \
  --servers 1 \
  --api-port 6443 \
  --k3s-arg "--disable=traefik@server:*" \
  --k3s-arg "--disable=servicelb@server:*" \
  --k3s-arg "--disable=coredns@server:*" \
  --wait

k3d kubeconfig get seccluster > ~/.kube/config
echo "Cluster ready! Run: kubectl get nodes"

# echo "Installing latest Kyverno..."
# helm repo add kyverno https://kyverno.github.io/kyverno/ 2>/dev/null || true
# helm repo update
# helm upgrade --install kyverno kyverno/kyverno \
#   --namespace kyverno --create-namespace \
#   --wait --timeout 5m

# echo "Waiting for Kyverno CRDs..."
# kubectl wait --for condition=established crd/clusterpolicies.kyverno.io --timeout=120s

# echo "Applying all 10 security policies..."
# kubectl apply -f ../kyverno-policies/clusterpolicies/ > /dev/null

# echo ""
# echo "DONE! Your zero-trust Kubernetes cluster is ready."
# echo "→ 1 node running"
# echo "→ Kyverno installed"
# echo "→ All 10 policies enforced (privileged pods, :latest tags, etc. BLOCKED)"
# echo ""
# echo "Try this now:"
# echo "kubectl run bad --image=nginx:latest --restart=Never"
# echo "→ Should be instantly denied by your policies"
# echo ""
