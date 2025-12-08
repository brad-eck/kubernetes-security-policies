# kubernetes-security-policies

My personal zero-trust Kubernetes playground.

## What’s actually in here right now

- `cluster/create.sh` → 60-second one-liner that gives me a clean, minimal k3s cluster (single container, no CoreDNS, no Traefik, no ServiceLB). I run this multiple times a day.
- Kyverno 1.12+ with 10 (soon 25+) battle-tested ClusterPolicies that:
  - Enforce Pod Security Standards – Baseline (no privileged, no host namespaces, no dangerous caps)
  - Block `:latest` tags
  - Require resource requests/limits and governance labels
  - Auto-mutate `imagePullPolicy: IfNotPresent`, drop ALL capabilities, force runAsNonRoot
  - …and a bunch more coming (Cosign verification, hostPath blocking, approved registries, etc.)

Run yourself:

```bash
git clone https://github.com/brad-eck/kubernetes-security-policies.git
cd kubernetes-security-policies/cluster
./create.sh          # ~60 seconds later you have a fully armed cluster
kubectl run evil --image=nginx:latest --privileged --restart=Never
# → instantly denied by my policies
