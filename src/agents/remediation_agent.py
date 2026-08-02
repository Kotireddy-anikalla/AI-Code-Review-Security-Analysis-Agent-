import json
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class RemediationAgent:
    """Generates specific fix recommendations with corrected code examples and best practice explanations per finding."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0.1)

    def generate_remediations(self, code: str, language: str, findings: list) -> list:
        if not findings:
            return []

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Remediation Agent.
Review the provided original source code and the list of detected code findings (quality issues and security vulnerabilities).
For each finding, generate specific fix recommendations, a clear explanation, and the exact corrected code example.

Return ONLY a valid JSON array matching this exact schema:
[
  {
    "type": "Name of issue being fixed",
    "severity": "CRITICAL",
    "line": null,
    "explanation": "Clear explanation of how and why the fix works securely",
    "corrected_code": "Exact corrected code snippet or function rewrite"
  }
]"""),
            ("user", "Language: {language}\n\nOriginal Code:\n
