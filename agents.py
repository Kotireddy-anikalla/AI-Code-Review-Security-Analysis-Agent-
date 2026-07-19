import ast
import re
import javalang
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class Finding:
    type: str          # "code_smell", "vulnerability"
    severity: str      # "Critical", "High", "Medium", "Low"
    description: str
    line: int
    suggestion: str = ""

class CodeAnalysisAgent:
    def analyze(self, code: str, language: str) -> List[Finding]:
        if language == "python":
            return self._analyze_python(code)
        elif language == "java":
            return self._analyze_java(code)
        return []

    def _analyze_python(self, code: str) -> List[Finding]:
        findings = []
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return findings

        # 1. Long method detection (> 20 lines)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines = node.end_lineno - node.lineno + 1
                if lines > 20:
                    findings.append(Finding(
                        type="code_smell",
                        severity="Medium",
                        description=f"Function '{node.name}' is too long ({lines} lines)",
                        line=node.lineno,
                        suggestion="Refactor into smaller helper functions."
                    ))

        # 2. Too many parameters (> 5)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.args.args) > 5:
                    findings.append(Finding(
                        type="code_smell",
                        severity="Medium",
                        description=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                        line=node.lineno,
                        suggestion="Combine parameters into a data class or use keyword arguments."
                    ))

        # 3. Hardcoded secrets (simple regex)
        for i, line in enumerate(code.splitlines(), start=1):
            if re.search(r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]", line, re.I):
                findings.append(Finding(
                    type="vulnerability",
                    severity="Critical",
                    description="Hardcoded secret detected",
                    line=i,
                    suggestion="Move to environment variables or a secrets manager."
                ))

        # 4. SQL injection risk (string concatenation in SQL)
        for node in ast.walk(tree):
            if isinstance(node, ast.Str) and "sql" in node.s.lower():
                # simplistic – look for concatenation
                # We'll check parent for BinOp
                parent = getattr(node, 'parent', None)
                if parent and isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Add):
                    findings.append(Finding(
                        type="vulnerability",
                        severity="High",
                        description="Possible SQL injection via string concatenation",
                        line=node.lineno,
                        suggestion="Use parameterized queries or ORM."
                    ))
        return findings

    def _analyze_java(self, code: str) -> List[Finding]:
        findings = []
        try:
            tree = javalang.parse.parse(code)
        except Exception:
            return findings

        # 1. Long method detection (> 20 lines) – walk through methods
        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                # approximate line count from position
                if node.position:
                    # simplistic – better to count lines in code
                    lines = code.count('\n', node.position.line, -1)  # not perfect
                    # estimate: we'll just count body lines
                    body_lines = len(str(node.body).splitlines()) if node.body else 0
                    if body_lines > 20:
                        findings.append(Finding(
                            type="code_smell",
                            severity="Medium",
                            description=f"Method '{node.name}' is too long ({body_lines} lines)",
                            line=node.position.line if node.position else 1,
                            suggestion="Refactor into smaller methods."
                        ))

        # 2. Hardcoded secrets
        for i, line in enumerate(code.splitlines(), start=1):
            if re.search(r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]", line, re.I):
                findings.append(Finding(
                    type="vulnerability",
                    severity="Critical",
                    description="Hardcoded secret detected",
                    line=i,
                    suggestion="Use environment variables or a secrets manager."
                ))

        # 3. SQL injection via string concatenation
        for i, line in enumerate(code.splitlines(), start=1):
            if re.search(r"(Statement|PreparedStatement).*\"\s*\+\s*", line):
                findings.append(Finding(
                    type="vulnerability",
                    severity="High",
                    description="Possible SQL injection via string concatenation",
                    line=i,
                    suggestion="Use PreparedStatement with parameter binding."
                ))

        return findings


class SecurityVulnerabilityAgent:
    def scan(self, code: str, language: str) -> List[Finding]:
        # We already include security findings in CodeAnalysisAgent,
        # but we separate them for clarity. We'll reuse the same detection.
        # For this milestone, we simply call CodeAnalysisAgent and filter.
        ca = CodeAnalysisAgent()
        all_findings = ca.analyze(code, language)
        return [f for f in all_findings if f.type == "vulnerability"]


def orchestrate_agents(code: str, language: str) -> Dict[str, Any]:
    """Run both agents in parallel and merge results."""
    import concurrent.futures
    ca = CodeAnalysisAgent()
    sa = SecurityVulnerabilityAgent()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_ca = executor.submit(ca.analyze, code, language)
        future_sa = executor.submit(sa.scan, code, language)
        ca_findings = future_ca.result()
        sa_findings = future_sa.result()

    # Merge (avoid duplicates by comparing line and description)
    merged = ca_findings + [f for f in sa_findings if f not in ca_findings]
    # Sort by severity (Critical > High > Medium > Low)
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    merged.sort(key=lambda f: severity_order.get(f.severity, 4))

    return {
        "findings": [asdict(f) for f in merged],
        "summary": {
            "total": len(merged),
            "critical": sum(1 for f in merged if f.severity == "Critical"),
            "high": sum(1 for f in merged if f.severity == "High"),
            "medium": sum(1 for f in merged if f.severity == "Medium"),
            "low": sum(1 for f in merged if f.severity == "Low"),
        }
    }
