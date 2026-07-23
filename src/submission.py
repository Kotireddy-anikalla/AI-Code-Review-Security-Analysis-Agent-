
import ast
import javalang
from typing import Dict, Tuple, Union

class CodeSubmissionHandler:
    """Handles direct code submission and file uploads for Python and Java with syntax validation."""

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
            javalang.parser.parse(code)
            return True, "Valid Java syntax."
        except Exception as e:
            return False, f"Java Syntax Error: {str(e)}"

    def process_submission(self, code_content: str, language: str) -> Dict[str, Union[bool, str]]:
        language = language.lower()
        if language == "python":
            is_valid, msg = self.validate_python_syntax(code_content)
        elif language == "java":
            is_valid, msg = self.validate_java_syntax(code_content)
        else:
            return {"valid": False, "message": f"Unsupported language: {language}", "language": language}

        return {
            "valid": is_valid,
            "message": msg,
            "language": language,
            "code": code_content
        }
