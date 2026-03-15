# RBAC Configuration

Role-Based Access Control manifests implementing defense-in-depth for cluster access.

## Design Principles

1. **Least privilege** — every role grants the minimum verbs and resources required for its persona. No wildcard rules outside of the break-glass cluster-admin.
2. **Separation of duties** — developers cannot modify RBAC or NetworkPolicies. CI/CD can push secrets but not read them. Auditors can read everything but change nothing.
3. **Group-based binding** — human users are bound via IdP groups, never individual usernames, so access stays in sync with team membership.
4. **Service account isolation** — every workload and automation pipeline gets a dedicated ServiceAccount with `automountServiceAccountToken: false` by default.
5. **Aggregated roles** — new CRD visibility (Kyverno, cert-manager, etc.) is added via labeled fragments that automatically compose into parent roles.
6. **Escalation prevention** — a Kyverno policy blocks creation of Roles/ClusterRoles with wildcard rules, closing the most common privilege escalation vector.

## Files

| File | Purpose |
|------|---------|
| `00-service-accounts.yaml` | Dedicated ServiceAccounts for workloads and automation |
| `01-clusterroles.yaml` | ClusterRole definitions for each persona |
| `02-clusterrolebindings.yaml` | Cluster-scoped bindings (monitoring, auditing, admin) |
| `03-namespace-bindings.yaml` | Namespace-scoped RoleBindings (production, staging) |
| `04-aggregated-roles.yaml` | Aggregated ClusterRoles with composable fragments |
| `05-deny-escalation.yaml` | Escalation prevention roles and Kyverno policy |

## Personas

| Role | Scope | Can | Cannot |
|------|-------|-----|--------|
| **Cluster Admin** | Cluster | Everything (break-glass) | N/A |
| **Namespace Admin** | Namespace | Full namespace control, view RBAC | Modify RBAC, access other namespaces |
| **Developer** | Namespace | Deploy, scale, view logs, manage ConfigMaps | Read Secrets, modify RBAC/NetworkPolicies |
| **CI/CD Deployer** | Namespace | Create/update workloads, push secrets | Read secrets, exec into pods |
| **Monitoring** | Cluster | Read pods/nodes/services, scrape metrics | Modify anything |
| **Security Auditor** | Cluster | Read all resources, RBAC, policy reports | Modify anything, read secret data |
| **Log Collector** | Cluster | Read pods and pod logs | Everything else |

## Usage

```bash
# Apply all RBAC resources
kubectl apply -f rbac/

# Verify roles
kubectl get clusterroles -l app.kubernetes.io/managed-by=kubernetes-security-policies

# Audit bindings
kubectl get clusterrolebindings,rolebindings -A -l app.kubernetes.io/managed-by=kubernetes-security-policies

# Check effective permissions for a user
kubectl auth can-i --list --as=user@example.com

# Check effective permissions for a service account
kubectl auth can-i --list --as=system:serviceaccount:production:ci-deploy
```

## Extending

To add a new namespace, copy the relevant RoleBindings from `03-namespace-bindings.yaml` and update the `namespace` field. The ClusterRole references stay the same.

To add visibility for a new CRD, create a labeled ClusterRole fragment (see `04-aggregated-roles.yaml`) and it will automatically compose into the `security-custom-view` parent.
