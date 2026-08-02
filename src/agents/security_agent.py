import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class SecurityVulnerabilityAgent:
    """Scans submitted code for OWASP-standard vulnerabilities with severity scoring and location flagging."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0.0)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Security Vulnerability Agent. Scan the provided source code for OWASP vulnerabilities including:
- SQL Injection
- Cross-Site Scripting (XSS)
- Hardcoded Secrets / API Keys
- CSRF, Broken Access Control, Insecure Authentication

The "severity" field must be exactly one of these four values (uppercase, no synonyms like "Major"/"Minor"): CRITICAL, HIGH, MEDIUM, LOW.

Return ONLY a valid JSON array of objects with the exact following schema and no additional formatting or text:
[
  {{
    "vulnerability": "OWASP Category / Type",
    "severity": "CRITICAL",
    "line": null,
    "description": "Explanation of vulnerability and risk"
  }}
]"""),
            ("user", "Language: {language}\n\nCode:\n```{language}\n{code}\n```")
        ])
        self.chain = self.prompt | self.llm

    @staticmethod
    def _parse_response(response) -> list:
        if isinstance(response.content, list):
            raw_text = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content])
        else:
            raw_text = str(response.content)

        content = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(content)

    def analyze(self, code: str, language: str) -> list:
        """Synchronous analysis (blocking Groq call)."""
        try:
            response = self.chain.invoke({"language": language, "code": code})
            return self._parse_response(response)
        except Exception as e:
            return [{"vulnerability": "Security Analysis Error", "severity": "LOW", "line": None, "description": str(e)}]

    async def analyze_async(self, code: str, language: str) -> list:
        """Async analysis, so this agent can run concurrently with CodeAnalysisAgent."""
        try:
            response = await self.chain.ainvoke({"language": language, "code": code})
            return self._parse_response(response)
        except Exception as e:
            return [{"vulnerability": "Security Analysis Error", "severity": "LOW", "line": None, "description": str(e)}]
