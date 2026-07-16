# AI-Code-Review-Security-Analysis-Agent-
 The objective of this project is to develop an AI Code Review &amp; Security Analysis Agent — an
intelligent multi-agent platform that automatically analyzes source code for quality issues, security
vulnerabilities, and best practice violations. A developer pastes code directly or uploads a source file
in Python or Java; a multi-agent pipeline triggers automatically — a Code Analysis Agent reviews
code structure, detects code smells and design issues, a Security Vulnerability Agent scans for
OWASP-standard vulnerabilities including SQL injection, XSS, hardcoded secrets, and broken access
controls, a Remediation Agent generates specific fix recommendations with corrected code
examples, and a PR Summary Agent produces a human-readable review summary. A RAG-powered
Conversational Code Assistant allows developers to ask follow-up questions about flagged issues,
request deeper explanations, or query best practice guidelines — all grounded in an indexed secure
coding knowledge base. Results are presented in a clean developer portal with severity-scored
findings, remediation guidance, and exportable review reports.
## milestone -1
1. Study OWASP vulnerability standards, secure coding guidelines, code smell patterns, and
RAG architecture.
2. Design system architecture, agent responsibilities, orchestration flow, and data models.
3. Develop Code Submission Module — support direct code paste and file upload for Python
and Java with syntax validation.
4. Build Secure Coding Knowledge Base — index OWASP guidelines, secure coding standards,
and best practice documents into RAG pipeline via chunking, embedding, and vector store
indexing.
#### FILES
main.py :- This is the main application that serves two REST endpoints:
/api/submit – accepts code (pasted or uploaded), validates syntax for Python/Java, and returns success/error status.
/api/chat – accepts a natural‑language question about secure coding, retrieves relevant knowledge chunks, and generates an answer using a local Hugging Face LLM.

build_kb.py :- This script creates and persists a vector store (Chroma) from the secure‑coding knowledge text (knowledge.txt). It is run once before starting the main server.

requirements.txt :- Contains all the requirements to run the code.

knowledge.txt :- contains the data about secure coding practices and owasp top 10 policies, etc.

## Prerequisites
- Python
- Java javac
- HuggingFace account & token (free) – get from huggingface.co/settings/tokens

## Setup
```bash
pip install -r requirements.txt
python build_kb.py
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
