# kubernetes-security-policies

My personal zero-trust Kubernetes playground.

## What’s actually in here right now

- Kyverno 1.12+ with battle-tested ClusterPolicies that:
  - Enforce Pod Security Standards – Baseline (no privileged, no host namespaces, no dangerous caps)
  - Block `:latest` tags
  - Require resource requests/limits and governance labels
  - Auto-mutate `imagePullPolicy: IfNotPresent`, drop ALL capabilities, force runAsNonRoot

## Requirements:
- Running k8s cluster
- Kyverno deployed in your cluster

Run yourself:

```bash
git clone https://github.com/brad-eck/kubernetes-security-policies.git
cd kubernetes-security-policies
kubectl apply -f ./kyverno-policies/clusterpolicies/

# Test working good pod
kubectl apply -f ./cluster/test/good-pod.yaml
# Test bad pod. Should fail to create
kubectl apply -f ./cluster/test/bad-pod.yaml
```

## Running the Report Script:
This Python script generates an audit-ready HTML report from Kyverno PolicyReports, showing policy status and violations mapped to compliance frameworks.

```bash
cd cli
python3 -m venv venv
source venv/bin/activate

pip install rich

./compliance_report.py
```

The report is saved to reports/compliance_report.html — open it in your browser.
