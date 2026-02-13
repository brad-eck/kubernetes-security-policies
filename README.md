# Kubernetes Security Policies with Kyverno

A production-ready collection of Kyverno policies for enforcing security best practices on Kubernetes clusters. This repository implements a defense-in-depth approach using policy-as-code to secure K3s and Kubernetes workloads.

## Overview

This project provides a comprehensive security policy framework using Kyverno, a Kubernetes-native policy engine. The policies enforce Pod Security Standards, image verification, resource governance, and compliance requirements without requiring webhook configurations or separate policy servers.

### Key Features

- **Pod Security Standards Enforcement**: Implements baseline security controls preventing privileged containers, host namespace access, and dangerous capabilities
- **Image Security**: Blocks `:latest` tags and enforces cosign keyless signature verification
- **Resource Governance**: Mandates resource requests/limits and governance labels
- **Automatic Remediation**: Mutates workloads to apply security defaults (drop capabilities, enforce non-root execution)
- **Compliance Reporting**: Python-based CLI tool generates HTML audit reports mapping policy violations to compliance frameworks

## Repository Structure

```
.
├── kyverno-policies/
│   └── clusterpolicies/           # Kyverno ClusterPolicy definitions
├── cli/                           # Compliance reporting tools
├── cluster/
│   └── tests/                      # Test pod manifests (good/bad examples)
│     └── bad-pod.yaml             # Bad pod example
|     └── good-pod.yaml            # Good pod example
|     └── test-policies.py         # Test script for pod deployments
├── ARCHITECTURE.md                # System design documentation
├── COMPLIANCE_MAPPING.md          # Policy-to-framework mapping
└── README.md
```

## Prerequisites

- Kubernetes cluster (tested on K3s)
- Kyverno 1.12 or higher installed
- `kubectl` configured with cluster access
- Python 3.8+ (for compliance reporting)

### Installing Kyverno

```bash
# Install Kyverno via Helm
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update
helm install kyverno kyverno/kyverno -n kyverno --create-namespace

# Or via kubectl
kubectl create -f https://github.com/kyverno/kyverno/releases/download/v1.12.0/install.yaml
```

## Quick Start

### 1. Deploy Security Policies

```bash
# Clone the repository
git clone https://github.com/brad-eck/kubernetes-security-policies.git
cd kubernetes-security-policies

# Apply all ClusterPolicies
kubectl apply -f ./kyverno-policies/clusterpolicies/
```

### 2. Verify Policy Installation

```bash
# List installed policies
kubectl get clusterpolicies

# Check policy status
kubectl describe clusterpolicy <policy-name>
```

### 3. Test Policy Enforcement

```bash
# Test with a compliant pod (should succeed)
kubectl apply -f ./cluster/test/good-pod.yaml

# Test with a non-compliant pod (should fail)
kubectl apply -f ./cluster/test/bad-pod.yaml
```

## Policy Categories

### Security Enforcement Policies

**Baseline Pod Security**
- Blocks privileged containers
- Prevents host namespace sharing (PID, IPC, network)
- Restricts host path volumes
- Enforces security context constraints

**Capabilities Management**
- Drops all Linux capabilities by default
- Restricts addition of dangerous capabilities (NET_RAW, SYS_ADMIN, etc.)
- Validates securityContext settings

**Image Security**
- Blocks `:latest` image tags
- Requires valid cosign signatures (keyless verification)
- Enforces `imagePullPolicy: IfNotPresent`

### Governance Policies

**Resource Requirements**
- Mandates CPU and memory requests
- Mandates CPU and memory limits
- Prevents unbounded resource consumption

**Labeling Standards**
- Requires governance labels (owner, team, environment, app)
- Validates label format and values

### Mutation Policies

**Automatic Security Hardening**
- Sets `runAsNonRoot: true`
- Drops all capabilities automatically
- Configures `imagePullPolicy: IfNotPresent`
- Applies read-only root filesystem where applicable

## Compliance Reporting

The repository includes a Python CLI tool that generates audit-ready HTML reports from Kyverno PolicyReports, and a Python script that tests pod examples that can be found in `/tests`.

### Setup

```bash
cd cli
python3 -m venv venv
source venv/bin/activate
pip install rich
```

### Generate Report

```bash
./compliance_report.py
```

The report is saved to `reports/compliance_report.html` and includes:
- Policy compliance status by namespace
- Violation details with resource information
- Mapping to compliance frameworks (CIS, PCI-DSS, SOC 2, NIST)
- Color-coded status indicators

## Policy Modes

Kyverno policies support multiple enforcement modes:

- **Enforce**: Blocks non-compliant resources (default)
- **Audit**: Logs violations without blocking
- **Background**: Scans existing resources

To change a policy mode, edit the `validationFailureAction` field:

```yaml
spec:
  validationFailureAction: Audit  # or Enforce
```

## Customization

### Excluding Namespaces

Add namespace exclusions to policies:

```yaml
spec:
  match:
    any:
    - resources:
        kinds:
        - Pod
  exclude:
    any:
    - resources:
        namespaces:
        - kube-system
        - kyverno
```

### Adjusting Resource Requirements

Modify minimum resource requirements in resource governance policies:

```yaml
pattern:
  spec:
    containers:
    - resources:
        requests:
          memory: "128Mi"  # Adjust as needed
          cpu: "100m"
```

### Custom Image Registries

Update allowed registries in image verification policies:

```yaml
imageReferences:
- "docker.io/*"
- "gcr.io/my-project/*"
- "my-registry.example.com/*"
```

## Monitoring and Troubleshooting

### Check Policy Reports

```bash
# View policy reports in a namespace
kubectl get policyreport -n <namespace>

# Detailed report view
kubectl describe policyreport -n <namespace>
```

### View Policy Violations

```bash
# List all failures
kubectl get policyreport -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.summary.fail}{"\n"}{end}'
```

### Debug Policy Application

```bash
# Check Kyverno logs
kubectl logs -n kyverno -l app.kubernetes.io/name=kyverno

# View admission review events
kubectl get events --field-selector reason=PolicyViolation
```

## Best Practices

1. **Start with Audit Mode**: Test policies in audit mode before enforcing
2. **Gradual Rollout**: Apply policies to non-production namespaces first
3. **Exception Management**: Document and review namespace exclusions regularly
4. **Regular Reviews**: Audit policy reports weekly
5. **Update Policies**: Keep Kyverno and policies updated for latest security fixes

## Security Considerations

- **Policy Drift**: Regularly audit applied policies against repository
- **Admission Control**: Kyverno policies run in admission control path; ensure high availability
- **Resource Impact**: Monitor Kyverno resource consumption in large clusters
- **Privilege Escalation**: Protect Kyverno namespace with strict RBAC
- **Image Verification**: Maintain cosign public keys securely
