import concurrent.futures
from typing import Dict, List, Any
from src.agents.code_analysis_agent import CodeAnalysisAgent
from src.agents.security_agent import SecurityVulnerabilityAgent
from src.agents.remediation_agent import RemediationAgent
from src.agents.pr_summary_agent import PRSummaryAgent

class MultiAgentOrchestrator:
    """Orchestrates multi-agent pipeline execution across Analysis, Security, Remediation, and PR Summary agents."""

    def __init__(self):
        self.code_analysis_agent = CodeAnalysisAgent()
        self.security_agent = SecurityVulnerabilityAgent()
        self.remediation_agent = RemediationAgent()
        self.pr_summary_agent = PRSummaryAgent()

    def run_pipeline(self, code: str, language: str) -> Dict[str, Any]:
        # Step 1: Run Code Analysis Agent and Security Vulnerability Agent in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_quality = executor.submit(self.code_analysis_agent.analyze, code, language)
            future_security = executor.submit(self.security_agent.analyze, code, language)

            quality_findings = future_quality.result()
            security_findings = future_security.result()

        # Step 2: Merge Findings into a unified list
        unified_findings = []

        for item in quality_findings:
            item["category"] = "Code Quality"
            unified_findings.append(item)

        for item in security_findings:
            item["category"] = "Security Vulnerability"
            item["type"] = item.get("vulnerability", item.get("type", "Security Issue"))
            unified_findings.append(item)

        # Step 3: Run Remediation Agent to generate refactored code fixes
        remediations = self.remediation_agent.generate_remediations(code, language, unified_findings)

        # Step 4: Run PR Summary Agent to compile the executive review summary
        pr_summary = self.pr_summary_agent.generate_summary(code, language, unified_findings, remediations)

        return {
            "findings": unified_findings,
            "remediations": remediations,
            "pr_summary": pr_summary,
            "quality_count": len(quality_findings),
            "security_count": len(security_findings),
            "total_issues": len(unified_findings)
        }
