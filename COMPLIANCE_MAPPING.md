# Compliance Control Mapping

This document maps the Kyverno policies in this repository to industry-recognized security frameworks and standards.

The goal is to demonstrate how the enforced controls reduce operational burden while satisfying auditor requirements for SOC 2, ISO 27001, NIST 800-53, PCI DSS, GDPR, and CIS Kubernetes Benchmark.

| Policy Name                        | Description                                      | CIS Kubernetes Benchmark | NIST 800-53     | SOC 2              | ISO 27001      | PCI DSS       | GDPR (Art.) |
|------------------------------------|--------------------------------------------------|--------------------------|-----------------|--------------------|----------------|---------------|-------------|
| pss-baseline                       | Official Pod Security Standards Baseline profile | 5.2.x (Pod Security)     | SC-7, AC-6      | CC6.1, CC6.6       | A.12.4.1       | 6.5.2         | -           |
| disallow-latest-tag                | Blocks `:latest` image tags                      | 5.1.2                    | SI-7            | CC6.8              | A.12.6.1       | 6.3.1         | -           |
| require-approved-registries        | Restricts images to trusted registries           | 5.1.3                    | SI-10           | CC7.1              | A.12.2.1       | 6.3.7         | -           |
| require-governance-labels          | Requires `app.kubernetes.io/team` label          | 5.7.4 (Metadata)         | AC-16           | CC6.1              | A.8.2.1        | 7.1.1         | -           |
| require-resource-limits            | Enforces CPU/memory requests & limits            | 5.7.1–5.7.3              | SC-6            | CC6.6              | A.12.1.2       | 6.5.2         | -           |
| drop-all-capabilities              | Drops all Linux capabilities + runAsNonRoot      | 5.2.8, 5.2.9             | AC-6            | CC6.1              | A.9.2.3        | 7.2.2         | -           |
| require-ifnotpresent               | Defaults imagePullPolicy + resource limits       | 5.1.2, 5.7.1             | SI-7            | CC6.6              | A.12.1.2       | 6.5.2         | -           |
| disallow-hostpath                  | Completely blocks hostPath volumes               | 5.2.5                    | SC-28           | CC6.1              | A.12.4.1       | 6.5.10        | -           |
| block-exec                         | Blocks kubectl exec/debug into pods              | 5.1.6                    | AC-3            | CC6.8              | A.9.4.4        | 7.2.3         | -           |
| require-cosign-keyless             | Requires Sigstore/Cosign keyless signatures      | -                        | SI-7(1), SA-22  | CC7.1              | A.12.2.1       | 6.3.7         | -           |

### Notes

- **CIS Kubernetes Benchmark** references are from v1.9.0 (current as of 2026).
- **NIST 800-53 Rev 5** controls are the most relevant matches.
- **SOC 2 Trust Services Criteria** focused on Security (Common Criteria).
- **ISO 27001:2022** Annex A controls.
- **PCI DSS v4.0** and **GDPR** mapped where direct relevance exists (e.g., access control, data protection).

These mappings can be used as evidence during audits to show automated enforcement without manual reviews.

Generated and maintained by Brady Eckman — January 2026.
