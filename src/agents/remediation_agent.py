import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class RemediationAgent:
    """Generates specific fix recommendations with corrected code examples and best practice explanations per finding."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0.1)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Remediation Agent.
Review the provided original source code and the list of detected code findings (quality issues and security vulnerabilities).
For each finding, generate specific fix recommendations, a clear explanation, and the exact corrected code example.

The "severity" field must be exactly one of these four values (uppercase, no synonyms like "Major"/"Minor"): CRITICAL, HIGH, MEDIUM, LOW. Carry over the same severity that was given for that finding.

Return ONLY a valid JSON array matching this exact schema, with no markdown fences and no extra commentary:
[
  {{
    "type": "Name of issue being fixed",
    "severity": "CRITICAL",
    "line": null,
    "explanation": "Clear explanation of how and why the fix works securely",
    "corrected_code": "Exact corrected code snippet or function rewrite"
  }}
]

Match the "type" value exactly to the corresponding finding's "type" field so results can be paired up downstream."""),
            ("user", """Language: {language}

Original Code:
{code}

Detected Findings:
{findings}

Generate the JSON array of remediations now.""")
        ])
        self.chain = self.prompt | self.llm

    def generate_remediations(self, code: str, language: str, findings: list) -> list:
        if not findings:
            return []

        findings_json = json.dumps(findings, indent=2)

        try:
            response = self.chain.invoke({
                "language": language,
                "code": code,
                "findings": findings_json,
            })

            if isinstance(response.content, list):
                raw_text = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content])
            else:
                raw_text = str(response.content)

            content = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
            remediations = json.loads(content)

            if not isinstance(remediations, list):
                raise ValueError("Expected a JSON array of remediation objects.")

            return remediations
        except Exception as e:
            return [{
                "type": "Remediation Generation Error",
                "severity": "LOW",
                "line": None,
                "explanation": str(e),
                "corrected_code": "",
            }]
