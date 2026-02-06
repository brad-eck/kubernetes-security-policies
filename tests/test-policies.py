#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path


class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'


class PolicyTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.expected_failures = 0

    def run_command(self, cmd):
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"

    def test_good_pod(self, pod_file):
        pod_name = Path(pod_file).stem
        
        print(f"{Colors.YELLOW}Testing compliant pod: {pod_name}{Colors.NC}")
        
        cmd = f"kubectl apply -f {pod_file} --dry-run=server"
        returncode, stdout, stderr = self.run_command(cmd)
        
        output = stdout + stderr
        
        if returncode == 0 or "created" in output or "configured" in output:
            print(f"{Colors.GREEN}PASS: Pod was accepted by policies{Colors.NC}\n")
            self.passed += 1
            
            cleanup_cmd = f"kubectl delete -f {pod_file} --ignore-not-found=true"
            self.run_command(cleanup_cmd + " > /dev/null 2>&1")
            return True
        else:
            print(f"{Colors.RED}FAIL: Compliant pod was rejected{Colors.NC}")
            print(f"Output: {output}\n")
            self.failed += 1
            return False

    def test_bad_pod(self, pod_file):
        pod_name = Path(pod_file).stem
        
        print(f"{Colors.YELLOW}Testing non-compliant pod: {pod_name}{Colors.NC}")
        
        cmd = f"kubectl apply -f {pod_file} --dry-run=server"
        returncode, stdout, stderr = self.run_command(cmd)
        
        output = (stdout + stderr).lower()
        
        rejection_keywords = ["denied", "blocked", "failed", "violated", "error"]
        
        if any(keyword in output for keyword in rejection_keywords):
            print(f"{Colors.GREEN}PASS: Pod was correctly rejected by policies{Colors.NC}")
            
            policy_lines = [line for line in (stdout + stderr).split('\n') 
                          if 'policy' in line.lower() or 'denied' in line.lower()]
            for line in policy_lines:
                print(f"  -> {line.strip()}")
            
            print()
            self.expected_failures += 1
            return True
        else:
            print(f"{Colors.RED}FAIL: Non-compliant pod was NOT rejected{Colors.NC}")
            print(f"Output: {stdout + stderr}\n")
            self.failed += 1
            return False

    def check_prerequisites(self):
        print(f"{Colors.BLUE}Checking prerequisites...{Colors.NC}")
        
        returncode, _, _ = self.run_command("which kubectl > /dev/null 2>&1")
        if returncode != 0:
            print(f"{Colors.RED}kubectl not found{Colors.NC}")
            return False
        
        returncode, _, _ = self.run_command("kubectl get nodes > /dev/null 2>&1")
        if returncode != 0:
            print(f"{Colors.RED}Cannot connect to Kubernetes cluster{Colors.NC}")
            return False
        
        returncode, stdout, _ = self.run_command("kubectl get clusterpolicies --no-headers 2>/dev/null")
        if returncode != 0:
            print(f"{Colors.RED}Kyverno not installed (no ClusterPolicies found){Colors.NC}")
            return False
        
        policy_count = len([line for line in stdout.split('\n') if line.strip()])
        print(f"{Colors.GREEN}Found {policy_count} ClusterPolicies{Colors.NC}\n")
        
        return True

    def run_tests(self):
        print(f"{Colors.BLUE}================================{Colors.NC}")
        print(f"{Colors.BLUE}Kyverno Policy Test Suite{Colors.NC}")
        print(f"{Colors.BLUE}================================{Colors.NC}\n")
        
        if not self.check_prerequisites():
            return 1
        
        print(f"{Colors.BLUE}Running compliance tests...{Colors.NC}\n")
        
        if os.path.exists("good-pod.yaml"):
            self.test_good_pod("good-pod.yaml")
        else:
            print(f"{Colors.YELLOW}good-pod.yaml not found{Colors.NC}\n")
        
        if os.path.exists("bad-pod.yaml"):
            self.test_bad_pod("bad-pod.yaml")
        else:
            print(f"{Colors.YELLOW}bad-pod.yaml not found{Colors.NC}\n")
        
        bad_pod_files = list(Path('.').glob('bad-pod-*.yaml'))
        for bad_file in sorted(bad_pod_files):
            self.test_bad_pod(str(bad_file))
        
        self.print_summary()
        
        return 0 if self.failed == 0 else 1

    def print_summary(self):
        total = self.passed + self.expected_failures + self.failed
        
        print(f"{Colors.BLUE}================================{Colors.NC}")
        print(f"{Colors.BLUE}Test Summary{Colors.NC}")
        print(f"{Colors.BLUE}================================{Colors.NC}")
        print(f"{Colors.GREEN}Passed: {self.passed}{Colors.NC}")
        print(f"{Colors.GREEN}Expected rejections: {self.expected_failures}{Colors.NC}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.NC}")
        print(f"{Colors.BLUE}Total: {total}{Colors.NC}\n")
        
        if self.failed > 0:
            print(f"{Colors.RED}Some tests failed{Colors.NC}")
        else:
            print(f"{Colors.GREEN}All tests passed{Colors.NC}")


def main():
    tester = PolicyTester()
    exit_code = tester.run_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()