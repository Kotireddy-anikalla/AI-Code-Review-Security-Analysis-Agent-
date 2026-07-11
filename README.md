# AI-Code-Review-Security-Analysis-Agent-

## Prerequisites
- Python
- Java javac
- HuggingFace account & token (free) – get from huggingface.co/settings/tokens

## Setup
```bash
export HUGGINGFACEHUB_API_TOKEN="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"
pip install -r requirements.txt
python build_kb.py
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
