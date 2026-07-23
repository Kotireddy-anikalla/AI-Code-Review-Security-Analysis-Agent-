import streamlit as st
import os
from src.submission import CodeSubmissionHandler
from src.orchestration import MultiAgentOrchestrator
from src.rag_pipeline import KnowledgeBaseRAG
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="AI Code Review & Security Analysis Agent", layout="wide")

st.title("🛡️ AI Code Review & Security Analysis Portal")
st.markdown("Automated multi-agent code analysis powered by **Google Gemini API**.")

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

# Maintain a session state variable to store findings context for the chat
if "last_findings" not in st.session_state:
    st.session_state.last_findings = ""

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

            # Store in session state for chat contextual awareness
            st.session_state.last_findings = str(results["findings"])

            for issue in results["findings"]:
                severity = issue.get("severity", "LOW")
                color = "🔴" if severity in ["CRITICAL", "HIGH"] else "🟡" if severity == "MEDIUM" else "🔵"

                with st.expander(f"{color} [{issue['category']}] {issue.get('type', 'Issue')} - Severity: {severity}"):
                    st.write(f"**Line Number:** {issue.get('line', 'N/A')}")
                    st.write(f"**Description:** {issue.get('description')}")

# 💬 Conversational Code Assistant Section
st.header("💬 Conversational Code Assistant")
st.markdown("Ask follow-up questions about flagged issues, secure coding standards, or mitigation techniques.")

# Initialize chat history array if not already done
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display previous messages
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if user_query := st.chat_input("e.g., how can i stop sql injection?"):
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("Please provide your Gemini API key in the sidebar first.")
    else:
        # 1. Append User Message
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # 2. RAG Retrieval from Secure Coding Knowledge Base
        with st.spinner("Consulting secure coding knowledge base..."):
            try:
                rag = KnowledgeBaseRAG()
                relevant_docs = rag.query_knowledge_base(user_query, k=2)
                context_str = "\n\n".join([doc.page_content for doc in relevant_docs])
            except Exception:
                context_str = "No vector database context available. Rely on standard secure coding defaults."

        # 3. Query Gemini with RAG Context + Code Context
        llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash", temperature=0.2)
        
        chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert secure coding assistant. Answer the user's inquiry regarding code quality or security vulnerabilities.
            
            Use the following indexed secure coding knowledge base snippets to formulate your reply:
            ---
            {context}
            ---
            
            Context of recently scanned code findings:
            {findings_context}"""),
            ("user", "{question}")
        ])
        
        chain = chat_prompt | llm
        response = chain.invoke({
            "context": context_str,
            "findings_context": st.session_state.last_findings,
            "question": user_query
        })
        
        # Safe text string conversion handling
        if isinstance(response.content, list):
            bot_reply = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content])
        else:
            bot_reply = str(response.content)

        # 4. Append and Display Assistant Response
        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
