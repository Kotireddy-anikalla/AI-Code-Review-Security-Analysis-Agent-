import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class PRSummaryAgent:
    """Compiles all agent findings into a structured, human-readable pull request style review summary."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0.2)

    def generate_summary(self, code: str, language: str, findings: list, remediations: list) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert PR Summary Agent.
Compile all code analysis findings, security vulnerabilities, and remediation recommendations into a clean, structured, and professional Pull Request style review summary.

Structure the review summary with:
1. Executive Summary & Code Health Score (0-100)
2. Severity & Category Breakdown Table
3. Key Security & Quality Risks
4. Prioritized Remediation Action Plan"""),
            ("user", "Language: {language}\n\nFindings:\n{findings}\n\nRemediations:\n{remediations}")
        ])

        chain = prompt | self.llm
        try:
            response = chain.invoke({
                "language": language,
                "findings": str(findings),
                "remediations": str(remediations)
            })
            if isinstance(response.content, list):
                return "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content])
            return str(response.content)
        except Exception as e:
            return f"### PR Summary Generation Error\nCould not generate summary: {str(e)}"
