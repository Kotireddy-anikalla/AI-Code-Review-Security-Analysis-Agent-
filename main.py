import os
import ast
import tempfile
import subprocess
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.llms import HuggingFaceHub          # corrected import
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma          # corrected import
from langchain.embeddings import HuggingFaceEmbeddings

app = FastAPI()

@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check that the vector store exists (you must run build_kb.py first)
if not os.path.exists("./chroma_db"):
    raise RuntimeError("Chroma DB not found. Please run build_kb.py first.")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings,
    collection_name="secure_coding"
)

# Hugging Face Hub LLM (requires HUGGINGFACEHUB_API_TOKEN env variable)
llm = HuggingFaceHub(
    repo_id="google/flan-t5-large",
    task="text2text-generation",
    model_kwargs={"temperature": 0, "max_length": 512}
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(k=3),
    return_source_documents=True
)

submissions = {}

def validate_python(code):
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [f"Line {e.lineno}: {e.msg}"]

def validate_java(code):
    # Use a temporary file with a unique name
    with tempfile.NamedTemporaryFile(suffix=".java", delete=False) as f:
        f.write(code.encode('utf-8'))
        java_file = f.name
    try:
        result = subprocess.run(
            ["javac", java_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode != 0:
            return [result.stderr.strip()]
        return []
    finally:
        # Clean up temporary files
        if os.path.exists(java_file):
            os.unlink(java_file)
        class_file = java_file.replace(".java", ".class")
        if os.path.exists(class_file):
            os.unlink(class_file)

@app.post("/api/submit")
async def submit_code(
    code: str = Form(None),
    file: UploadFile = File(None),
    language: str = Form(...)
):
    if file:
        code = (await file.read()).decode('utf-8')
    if not code:
        raise HTTPException(status_code=400, detail="No code provided")

    lang = language.lower()
    if lang not in ["python", "java"]:
        raise HTTPException(status_code=400, detail="Unsupported language")

    errors = validate_python(code) if lang == "python" else validate_java(code)

    submission_id = str(uuid.uuid4())[:8]
    submissions[submission_id] = {
        "code": code,
        "language": lang,
        "errors": errors
    }

    return {
        "submission_id": submission_id,
        "status": "error" if errors else "success",
        "errors": errors,
        "lines": len(code.splitlines())
    }

@app.post("/api/chat")
async def chat(question: str = Form(...)):
    result = qa_chain.invoke({"query": question})   # .invoke() is recommended
    return {
        "answer": result["result"],
        "source_documents": [doc.page_content for doc in result["source_documents"]]
    }

@app.get("/api/health")
async def health():
    return {"status": "ok"}
