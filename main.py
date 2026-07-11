from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import ast
import subprocess
import uuid
from langchain.llms import HuggingFaceHub
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings

app = FastAPI()
@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

submissions = {}

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

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

@app.post("/api/submit")
async def submit_code(code: str = Form(None), file: UploadFile = File(None), language: str = Form(...)):
    if file:
        code = (await file.read()).decode('utf-8')
    errors = []
    if language == "python":
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Line {e.lineno}: {e.msg}")
    elif language == "java":
        with open("/tmp/Test.java", "w") as f:
            f.write(code)
        result = subprocess.run(["javac", "/tmp/Test.java"], capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(result.stderr)
    submission_id = str(uuid.uuid4())[:8]
    submissions[submission_id] = {"code": code, "language": language, "errors": errors}
    return {
        "submission_id": submission_id,
        "status": "error" if errors else "success",
        "errors": errors,
        "lines": len(code.splitlines())
    }
