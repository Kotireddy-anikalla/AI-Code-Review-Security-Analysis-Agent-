import ast
import javalang
import os
from typing import Dict, Tuple, Union

class CodeSubmissionHandler:
    """Handles direct code submission and file uploads with automatic language detection and syntax validation."""

    def detect_language(self, code_content: str, filename: str = None) -> str:
        """Automatically detects whether the provided code is Python or Java."""
        if filename:
            ext = os.path.splitext(filename)[1].lower()
            if ext in [".py", ".pyw"]:
                return "python"
            if ext in [".java"]:
                return "java"

        stripped = code_content.strip()

        # Check Java syntax signatures
        java_keywords = ["public class ", "public static void main", "import java.", "System.out.println", "private final ", "protected class "]
        if any(kw in code_content for kw in java_keywords):
            return "java"

        # Check Python syntax signatures
        python_keywords = ["def ", "import ", "from ", "class ", "elif ", "if __name__ == "]
        if stripped.startswith(("import ", "def ", "class ", "from ", "#")) or any(kw in code_content for kw in python_keywords):
            return "python"

        # AST Parse trial fallback
        try:
            ast.parse(code_content)
            return "python"
        except SyntaxError:
            try:
                if "class" in code_content or "public" in code_content:
                    javalang.parse.parse(code_content)
                return "java"
            except Exception:
                return "python"

    @staticmethod
    def validate_python_syntax(code: str) -> Tuple[bool, str]:
        try:
            ast.parse(code)
            return True, "Valid Python syntax."
        except SyntaxError as e:
            return False, f"Python Syntax Error on line {e.lineno}: {e.msg}"

    @staticmethod
    def validate_java_syntax(code: str) -> Tuple[bool, str]:
        try:
            if "class" in code or "public" in code:
                javalang.parse.parse(code)
            return True, "Valid Java syntax."
        except Exception as e:
            return False, f"Java Syntax Error: {str(e)}"

    def process_submission(self, code_content: str, filename: str = None) -> Dict[str, Union[bool, str]]:
        if not code_content.strip():
            return {"valid": False, "message": "Submission content is empty.", "language": "Unknown", "code": code_content}

        detected_lang = self.detect_language(code_content, filename)

        if detected_lang == "python":
            is_valid, msg = self.validate_python_syntax(code_content)
        elif detected_lang == "java":
            is_valid, msg = self.validate_java_syntax(code_content)
        else:
            return {"valid": False, "message": f"Unsupported language: {detected_lang}", "language": detected_lang.capitalize(), "code": code_content}

        return {
            "valid": is_valid,
            "message": msg,
            "language": detected_lang.capitalize(),
            "code": code_content
        }
