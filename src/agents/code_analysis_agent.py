import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

class CodeAnalysisAgent:
    """Detects code smells, complexity issues, design anti-patterns, and poor coding practices using Google Gemini."""

    def __init__(self, model_name: str = "gemini-3.5-flash"): # Or whichever model works for you
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.0)

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

        content = raw_text.strip().lstrip("```json").rstrip("```").strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return [{"type": "Format Error", "severity": "LOW", "line": None, "description": content}]
