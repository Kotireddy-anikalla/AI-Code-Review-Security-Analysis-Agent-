
import concurrent.futures
from typing import Dict, List, Any
from src.agents.code_analysis_agent import CodeAnalysisAgent
from src.agents.security_agent import SecurityVulnerabilityAgent

class MultiAgentOrchestrator:
    """Orchestrates multi-agent pipeline execution in parallel and merges outputs."""

    def __init__(self):
        self.code_analysis_agent = CodeAnalysisAgent()
        self.security_agent = SecurityVulnerabilityAgent()

    def run_pipeline(self, code: str, language: str) -> Dict[str, List[Any]]:
        # Run Code Analysis Agent and Security Vulnerability Agent in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_quality = executor.submit(self.code_analysis_agent.analyze, code, language)
            future_security = executor.submit(self.security_agent.analyze, code, language)

            quality_findings = future_quality.result()
            security_findings = future_security.result()

        # Merge findings into a unified output
        unified_findings = []

        for item in quality_findings:
            item["category"] = "Code Quality"
            unified_findings.append(item)

        for item in security_findings:
            item["category"] = "Security Vulnerability"
            item["type"] = item.get("vulnerability", "Security Issue")
            unified_findings.append(item)

        return {
            "findings": unified_findings,
            "quality_count": len(quality_findings),
            "security_count": len(security_findings),
            "total_issues": len(unified_findings)
        }
