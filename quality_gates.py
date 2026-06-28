# pickal — Quality Gates Configuration

## Overview

This document outlines the quality gates and automated checks for pickal.

## Quality Gates

### Code Quality

```yaml
code_quality:
  enable_ruff: true
  enable_mypy: true
  enable_black: true
  enable_isort: true
  enable_bandit: true
  enable_semgrep: true
  enable_pytest: true
  enable_coverage: true
  coverage_threshold: 80
```

### Documentation

```yaml
documentation:
  enable_pdoc: true
  enable_sphinx: true
  enable_readthedocs: true
  enable_doxygen: true
  enable_swagger: true
  enable_openapi: true
  enable_changelog: true
  enable_license: true
```

### Testing

```yaml
testing:
  enable_unit_tests: true
  enable_integration_tests: true
  enable_end_to_end_tests: true
  enable_performance_tests: true
  enable_security_tests: true
  enable_regression_tests: true
  enable_acceptance_tests: true
  enable_manual_tests: true
```

## Automated Checks

### Pre-commit Hooks

```yaml
pre_commit:
  enable_ruff: true
  enable_black: true
  enable_isort: true
  enable_bandit: true
  enable_semgrep: true
  enable_pytest: true
  enable_coverage: true
  enable_license_check: true
  enable_copyright_check: true
```

### CI/CD Pipeline

```yaml
ci_cd:
  enable_continuous_integration: true
  enable_continuous_deployment: true
  enable_automated_testing: true
  enable_automated_building: true
  enable_automated_deploying: true
  enable_automated_security_scanning: true
  enable_automated_performance_testing: true
  enable_automated_documentation: true
```

## Quality Metrics

### Code Metrics

```yaml
code_metrics:
  enable_sloc: true
  enable_complexity: true
  enable_duplication: true
  enable_cohesion: true
  enable_coupling: true
  enable_maintainability: true
  enable_reliability: true
  enable_security: true
```

### Test Metrics

```yaml
test_metrics:
  enable_coverage: true
  enable_assertions: true
  enable_mocks: true
  enable_fixtures: true
  enable_parameterization: true
  enable_tagging: true
  enable_parallel_execution: true
  enable_flaky_tests: true
```

## Quality Gates Configuration

### Gate Definitions

```yaml
gate_definitions:
  gate_1:
    name: "Basic Quality"
    checks:
      - "ruff_check"
      - "mypy_check"
      - "pytest_basic"
    threshold: 90
  
  gate_2:
    name: "Advanced Quality"
    checks:
      - "ruff_check"
      - "mypy_check"
      - "pytest_advanced"
      - "coverage_check"
    threshold: 95
  
  gate_3:
    name: "Production Quality"
    checks:
      - "ruff_check"
      - "mypy_check"
      - "pytest_production"
      - "coverage_check"
      - "security_check"
      - "performance_check"
    threshold: 100
```

## Quality Gates Implementation

### Gate 1: Basic Quality

```yaml
gate_1:
  name: "Basic Quality"
  description: "Basic code quality checks"
  checks:
    - name: "Code Style"
      tool: "ruff"
      command: "ruff check src tests"
      threshold: 0
    
    - name: "Type Checking"
      tool: "mypy"
      command: "mypy src"
      threshold: 0
    
    - name: "Basic Tests"
      tool: "pytest"
      command: "pytest -m basic"
      threshold: 80
```

### Gate 2: Advanced Quality

```yaml
gate_2:
  name: "Advanced Quality"
  description: "Advanced code quality checks"
  checks:
    - name: "Code Style"
      tool: "ruff"
      command: "ruff check src tests"
      threshold: 0
    
    - name: "Type Checking"
      tool: "mypy"
      command: "mypy src"
      threshold: 0
    
    - name: "Advanced Tests"
      tool: "pytest"
      command: "pytest -m advanced"
      threshold: 90
    
    - name: "Coverage"
      tool: "coverage"
      command: "coverage run -m pytest"
      threshold: 80
```

### Gate 3: Production Quality

```yaml
gate_3:
  name: "Production Quality"
  description: "Production-ready quality checks"
  checks:
    - name: "Code Style"
      tool: "ruff"
      command: "ruff check src tests"
      threshold: 0
    
    - name: "Type Checking"
      tool: "mypy"
      command: "mypy src"
      threshold: 0
    
    - name: "Production Tests"
      tool: "pytest"
      command: "pytest -m production"
      threshold: 95
    
    - name: "Coverage"
      tool: "coverage"
      command: "coverage run -m pytest"
      threshold: 90
    
    - name: "Security Check"
      tool: "bandit"
      command: "bandit -r src"
      threshold: 0
    
    - name: "Performance Check"
      tool: "pytest-benchmark"
      command: "pytest -m performance"
      threshold: 0
```

## Quality Gates Workflow

### Pre-commit Workflow

```yaml
pre_commit_workflow:
  stages:
    - name: "Code Quality"
      checks:
        - "ruff_check"
        - "black_check"
        - "isort_check"
    
    - name: "Security"
      checks:
        - "bandit_check"
        - "semgrep_check"
    
    - name: "Testing"
      checks:
        - "pytest_quick"
        - "coverage_quick"
```

### CI/CD Workflow

```yaml
ci_cd_workflow:
  stages:
    - name: "Build"
      checks:
        - "build_check"
        - "dependency_check"
    
    - name: "Test"
      checks:
        - "unit_tests"
        - "integration_tests"
        - "security_tests"
    
    - name: "Quality"
      checks:
        - "code_quality_check"
        - "coverage_check"
        - "documentation_check"
    
    - name: "Deploy"
      checks:
        - "deploy_check"
        - "smoke_test"
```

## Quality Gates Configuration

### Configuration File

```yaml
# quality_gates.yaml
quality_gates:
  gates:
    - name: "Basic Quality"
      level: 1
      checks: ["ruff", "mypy", "basic_tests"]
      threshold: 90
    
    - name: "Advanced Quality"
      level: 2
      checks: ["ruff", "mypy", "advanced_tests", "coverage"]
      threshold: 95
    
    - name: "Production Quality"
      level: 3
      checks: ["ruff", "mypy", "production_tests", "coverage", "security", "performance"]
      threshold: 100
  
  checks:
    ruff:
      tool: "ruff"
      command: "ruff check src tests"
      description: "Code style and linting"
    
    mypy:
      tool: "mypy"
      command: "mypy src"
      description: "Type checking"
    
    basic_tests:
      tool: "pytest"
      command: "pytest -m basic"
      description: "Basic tests"
    
    advanced_tests:
      tool: "pytest"
      command: "pytest -m advanced"
      description: "Advanced tests"
    
    production_tests:
      tool: "pytest"
      command: "pytest -m production"
      description: "Production tests"
    
    coverage:
      tool: "coverage"
      command: "coverage run -m pytest"
      description: "Test coverage"
    
    security:
      tool: "bandit"
      command: "bandit -r src"
      description: "Security scanning"
    
    performance:
      tool: "pytest-benchmark"
      command: "pytest -m performance"
      description: "Performance testing"
```

## Quality Gates Implementation

### Python Implementation

```python
# quality_gates.py
import subprocess
import json
from typing import Dict, List, Tuple

class QualityGate:
    """Quality gate implementation."""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def run_check(self, check_name: str) -> Tuple[bool, str]:
        """Run a quality check."""
        check = self.config["checks"].get(check_name)
        if not check:
            return False, f"Check {check_name} not found"
        
        try:
            result = subprocess.run(
                check["command"], 
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0, result.stdout
        except Exception as e:
            return False, str(e)
    
    def evaluate_gate(self, gate_name: str) -> Tuple[bool, Dict]:
        """Evaluate a quality gate."""
        gate = self.config["gates"].get(gate_name)
        if not gate:
            return False, {"error": f"Gate {gate_name} not found"}
        
        results = {}
        passed_checks = 0
        
        for check_name in gate["checks"]:
            passed, result = self.run_check(check_name)
            results[check_name] = {
                "passed": passed,
                "result": result
            }
            if passed:
                passed_checks += 1
        
        success_rate = (passed_checks / len(gate["checks"])) * 100
        passed = success_rate >= gate["threshold"]
        
        return passed, {
            "success_rate": success_rate,
            "passed": passed,
            "results": results
        }

# Example usage
if __name__ == "__main__":
    with open("quality_gates.yaml") as f:
        config = yaml.safe_load(f)
    
    gate = QualityGate(config)
    passed, result = gate.evaluate_gate("Production Quality")
    print(f"Gate passed: {passed}")
    print(json.dumps(result, indent=2))