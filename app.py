
import streamlit as st
import os
from src.submission import CodeSubmissionHandler
from src.orchestration import MultiAgentOrchestrator
from src.rag_pipeline import KnowledgeBaseRAG

st.set_page_config(page_title="AI Code Review & Security Analysis Agent", layout="wide")

st.title("🛡️ AI Code Review & Security Analysis Portal")
st.markdown("Automated multi-agent code analysis powered by **Google Gemini API** (Free Tier).")

# Sidebar - Settings
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Gemini API Key (Free)", type="password", help="Get a free key at https://aistudio.google.com/")
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key
    os.environ["GOOGLE_API_KEY"] = api_key

# Knowledge Base Initialization Button
if st.sidebar.button("Index Knowledge Base (RAG)"):
    try:
        rag = KnowledgeBaseRAG()
        rag.initialize_knowledge_base()
        st.sidebar.success("Knowledge Base Indexed Successfully (Free Local HuggingFace Embeddings)!")
    except Exception as e:
        st.sidebar.error(f"Error indexing KB: {str(e)}")

# Inputs
language = st.selectbox("Select Programming Language", ["Python", "Java"])
submission_mode = st.radio("Submission Mode", ["Direct Code Paste", "File Upload"])

code_content = ""
if submission_mode == "Direct Code Paste":
    code_content = st.text_area("Paste source code here...", height=250)
else:
    uploaded_file = st.file_uploader("Upload Python or Java File", type=["py", "java"])
    if uploaded_file is not None:
        code_content = uploaded_file.getvalue().decode("utf-8")

if st.button("Run Code Review & Security Analysis"):
    if not code_content.strip():
        st.warning("Please provide code input.")
    elif not os.environ.get("GEMINI_API_KEY"):
        st.error("Google Gemini API Key is missing. Please enter your free key in the sidebar.")
    else:
        submission_handler = CodeSubmissionHandler()
        val_result = submission_handler.process_submission(code_content, language)

        if not val_result["valid"]:
            st.error(f"Syntax Validation Failed: {val_result['message']}")
        else:
            st.success("Syntax Validation Passed. Executing Multi-Agent Pipeline...")

            orchestrator = MultiAgentOrchestrator()
            with st.spinner("Analyzing code with Gemini..."):
                results = orchestrator.run_pipeline(code_content, language)

            st.header("Unified Review Findings")
            st.metric("Total Issues Identified", results["total_issues"])

            for issue in results["findings"]:
                severity = issue.get("severity", "LOW")
                color = "🔴" if severity in ["CRITICAL", "HIGH"] else "🟡" if severity == "MEDIUM" else "🔵"

                with st.expander(f"{color} [{issue['category']}] {issue.get('type', 'Issue')} - Severity: {severity}"):
                    st.write(f"**Line Number:** {issue.get('line', 'N/A')}")
                    st.write(f"**Description:** {issue.get('description')}")
