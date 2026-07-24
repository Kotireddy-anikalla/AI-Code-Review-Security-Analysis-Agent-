import json
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

class CodeAnalysisAgent:
    """Detects code smells, complexity issues, design anti-patterns, and poor coding practices using Groq."""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile"):
        self.llm = ChatGroq(model_name=model_name, temperature=0.0)

    def analyze(self, code: str, language: str) -> list:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert Code Quality Agent. Analyze the source code for:
- Code smells
- Design anti-patterns (e.g., God Objects, Long Methods)
- Complexity issues
- Poor coding practices

Return ONLY a valid JSON array of objects with the exact following schema and no additional formatting or text:
[
  {{
    "type": "Code Quality / Anti-Pattern Name",
    "severity": "CRITICAL",
    "line": null,
    "description": "Detailed description of the issue"
  }}
]"""),
            ("user", "Language: {language}\n\nCode:\n```{language}\n{code}\n```")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"language": language, "code": code})
        
        # Safe text extraction from response
        if isinstance(response.content, list):
            raw_text = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content])
        else:
            raw_text = str(response.content)

        content = raw_text.strip().removeprefix("```json").removesuffix("```").strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return [{"type": "Format Error", "severity": "LOW", "line": None, "description": content}]
