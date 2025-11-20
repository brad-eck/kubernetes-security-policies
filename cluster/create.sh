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
