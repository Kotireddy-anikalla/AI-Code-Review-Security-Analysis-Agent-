
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

class SecurityVulnerabilityAgent:
    """Scans submitted code for OWASP-standard vulnerabilities with severity scoring and location flagging."""

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.0)

    def analyze(self, code: str, language: str) -> list:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Security Vulnerability Agent. Scan the provided source code for OWASP vulnerabilities including:
- SQL Injection
- Cross-Site Scripting (XSS)
- Hardcoded Secrets / API Keys
- CSRF, Broken Access Control, Insecure Authentication

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

        chain = prompt | self.llm
        response = chain.invoke({"language": language, "code": code})
        content = response.content.strip().lstrip("```json").rstrip("```").strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return [{"vulnerability": "Format Error", "severity": "LOW", "line": None, "description": content}]
