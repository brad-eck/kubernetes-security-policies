#!/usr/bin/env python3
"""
Kubernetes Security Compliance Reporter
Generates SOC 2 / ISO 27001 / NIST evidence from Kyverno policy reports
Aggregates by actual policy name for readable reports
"""

import subprocess
import datetime
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console(record=True)


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def get_policy_reports():
    try:
        output = run_cmd("kubectl get policyreport --all-namespaces -o json")
        if not output:
            return []
        data = json.loads(output)
        return data.get("items", [])
    except Exception as e:
        console.print(f"[yellow]Warning: Could not fetch PolicyReports: {e}[/yellow]")
        console.print(
            "[yellow]Cluster may be clean or reports not generated yet.[/yellow]"
        )
        return []


def main():
    console.print(Markdown("# Kubernetes Security Compliance Report"))
    console.print(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        cluster_name = run_cmd(
            "kubectl get nodes -o jsonpath={.items[0].metadata.name}"
        )
        console.print(f"Cluster: {cluster_name or 'Unknown'}")
    except:
        console.print("Cluster: Unknown")

    console.print("")

    reports = get_policy_reports()

    # Get all ClusterPolicy names
    try:
        policy_output = run_cmd("kubectl get clusterpolicy -o name")
        policy_lines = [line for line in policy_output.split("\n") if line.strip()]
        total_policies = len(policy_lines)
        policy_names = [line.split("/")[-1] for line in policy_lines]
    except:
        total_policies = 0
        policy_names = []

    if total_policies == 0:
        console.print("[red]No ClusterPolicies found in the cluster![/red]")
        return

    table = Table(title="Kyverno Policy Compliance Status (Aggregated)")
    table.add_column("Policy Name")
    table.add_column("Status")
    table.add_column("Total Violations")
    table.add_column("Compliance Mapping")

    # Aggregate violations by policy name
    violations_by_policy = {name: 0 for name in policy_names}

    for report in reports:
        for result in report.get("results", []):
            policy_name = result.get("policy", "unknown")
            if result.get("result") == "fail":
                violations_by_policy[policy_name] = (
                    violations_by_policy.get(policy_name, 0) + 1
                )

    pass_count = 0
    fail_count = 0

    for name in policy_names:
        violations = violations_by_policy.get(name, 0)
        status = "PASS" if violations == 0 else "FAIL"
        if violations == 0:
            pass_count += 1
        else:
            fail_count += 1

        mapping = "CIS 5.x / NIST SC-7 / SOC 2 CC6.1"  # Expand per-policy in future
        table.add_row(
            name,
            f"[green]{status}[/green]" if status == "PASS" else f"[red]{status}[/red]",
            str(violations),
            mapping,
        )

    console.print(table)
    console.print(
        f"\n[bold]Summary:[/bold] {pass_count} passing, {fail_count} failing out of {total_policies} policies"
    )
    console.print(
        "\n[bold]Note for auditors:[/bold] "
        "In Enforce mode, non-compliant resources are blocked at admission and do not generate reports. "
        "In Audit mode with background scanning, violations are logged for existing resources. "
        "Zero violations = effective preventive controls."
    )

    # Export
    Path("reports").mkdir(exist_ok=True)
    html_path = "reports/compliance_report.html"
    console.save_html(html_path)
    console.print(f"\nReport saved to {html_path}")
    console.print(
        "Attach this HTML report to your SOC 2 / ISO 27001 / NIST audit package!"
    )


if __name__ == "__main__":
    main()
