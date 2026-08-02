import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class SecurityVulnerabilityAgent:
    """Scans submitted code for OWASP-standard vulnerabilities with severity scoring and location flagging."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0.0)

    def analyze(self, code: str, language: str) -> list:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Security Vulnerability Agent. Scan the provided source code for OWASP vulnerabilities including:
- SQL Injection
- Cross-Site Scripting (XSS)
- Hardcoded Secrets / API Keys
- CSRF, Broken Access Control, Insecure Authentication

Return ONLY a valid JSON array of objects with the exact following schema and no additional formatting or text:
[
  {
    "vulnerability": "OWASP Category / Type",
    "severity": "CRITICAL",
    "line": null,
    "description": "Explanation of vulnerability and risk"
  }
]"""),
            ("user", "Language: {language}\n\nCode:\n```{language}\n{code}\n```")
        ])

        chain = prompt | self.llm
        try:
            response = chain.invoke({"language": language, "code": code})
            
            if isinstance(response.content, list):
                raw_text = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content])
            else:
                raw_text = str(response.content)

            content = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(content)
        except Exception as e:
            return [{"vulnerability": "Security Analysis Error", "severity": "LOW", "line": None, "description": str(e)}]
