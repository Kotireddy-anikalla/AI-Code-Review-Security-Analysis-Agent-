import asyncio
from typing import Dict, List, Tuple

from src.agents.code_analysis_agent import CodeAnalysisAgent
from src.agents.security_agent import SecurityVulnerabilityAgent
from src.agents.remediation_agent import RemediationAgent
from src.agents.pr_summary_agent import PRSummaryAgent


class MultiAgentOrchestrator:
    """Coordinates the Code Analysis, Security, Remediation, and PR Summary agents
    into a single unified code review pipeline.

    CodeAnalysisAgent and SecurityVulnerabilityAgent are independent of each other,
    so they run concurrently via asyncio. RemediationAgent and PRSummaryAgent each
    depend on the combined findings from the previous step, so they run sequentially
    after the analysis stage completes.
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.code_analysis_agent = CodeAnalysisAgent(model_name=model_name)
        self.security_agent = SecurityVulnerabilityAgent(model_name=model_name)
        self.remediation_agent = RemediationAgent(model_name=model_name)
        self.pr_summary_agent = PRSummaryAgent(model_name=model_name)

    # Canonical 4-tier severity scale used throughout the app.
    _VALID_SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}

    # Maps common synonyms / casings the LLM might still slip in, despite the
    # prompt's explicit enum instruction, onto the canonical scale.
    _SEVERITY_SYNONYMS = {
        "MAJOR": "HIGH",
        "MINOR": "LOW",
        "SEVERE": "CRITICAL",
        "BLOCKER": "CRITICAL",
        "MODERATE": "MEDIUM",
        "TRIVIAL": "LOW",
        "INFO": "LOW",
        "INFORMATIONAL": "LOW",
    }

    @classmethod
    def _normalize_severity(cls, raw_severity) -> str:
        """Coerces any severity value returned by an LLM into one of
        CRITICAL / HIGH / MEDIUM / LOW, regardless of casing or synonym drift."""
        if not raw_severity:
            return "MEDIUM"

        value = str(raw_severity).strip().upper()

        if value in cls._VALID_SEVERITIES:
            return value

        if value in cls._SEVERITY_SYNONYMS:
            return cls._SEVERITY_SYNONYMS[value]

        # Unrecognized value entirely (e.g. free-text) - default to a safe middle tier
        # rather than silently dropping the finding.
        return "MEDIUM"

    @classmethod
    def _normalize_quality_findings(cls, raw_findings: List[dict]) -> List[dict]:
        """Tags code-quality findings with category='Quality' and keeps the 'type' field as-is."""
        normalized = []
        for f in raw_findings:
            normalized.append({
                "category": "Quality",
                "type": f.get("type", "Unknown Issue"),
                "severity": cls._normalize_severity(f.get("severity")),
                "line": f.get("line"),
                "description": f.get("description", ""),
            })
        return normalized

    @classmethod
    def _normalize_security_findings(cls, raw_findings: List[dict]) -> List[dict]:
        """Tags security findings with category='Security' and renames 'vulnerability' -> 'type'
        so both finding types share one consistent key for downstream matching (e.g. remediations_map)."""
        normalized = []
        for f in raw_findings:
            normalized.append({
                "category": "Security",
                "type": f.get("vulnerability", f.get("type", "Unknown Vulnerability")),
                "severity": cls._normalize_severity(f.get("severity")),
                "line": f.get("line"),
                "description": f.get("description", ""),
            })
        return normalized

    async def _run_analysis_stage(self, code: str, language: str) -> Tuple[List[dict], List[dict]]:
        """Runs the code-quality and security analysis agents concurrently."""
        quality_raw, security_raw = await asyncio.gather(
            self.code_analysis_agent.analyze_async(code, language),
            self.security_agent.analyze_async(code, language),
        )
        return quality_raw, security_raw

    async def _run_pipeline_async(self, code: str, language: str) -> Dict:
        quality_raw, security_raw = await self._run_analysis_stage(code, language)

        quality_findings = self._normalize_quality_findings(quality_raw)
        security_findings = self._normalize_security_findings(security_raw)
        findings = quality_findings + security_findings

        # These two depend on the combined findings above, so they stay sequential.
        remediations = self.remediation_agent.generate_remediations(code, language, findings)
        for rem in remediations:
            if "severity" in rem:
                rem["severity"] = self._normalize_severity(rem.get("severity"))

        pr_summary = self.pr_summary_agent.generate_summary(code, language, findings, remediations)

        return {
            "findings": findings,
            "remediations": remediations,
            "pr_summary": pr_summary,
            "total_issues": len(findings),
            "quality_count": len(quality_findings),
            "security_count": len(security_findings),
        }

    def run_pipeline(self, code: str, language: str) -> Dict:
        """Synchronous entry point used by app.py (Streamlit callbacks are sync).
        Internally runs the analysis stage concurrently via asyncio."""
        return asyncio.run(self._run_pipeline_async(code, language))
