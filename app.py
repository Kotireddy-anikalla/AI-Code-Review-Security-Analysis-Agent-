import streamlit as st
import os
import json
from src.submission import CodeSubmissionHandler
from src.orchestration import MultiAgentOrchestrator
from src.rag_pipeline import KnowledgeBaseRAG
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

st.set_page_config(page_title="AI Code Review & Security Analysis Agent", layout="wide")

st.title("🛡️ AI Code Review & Security Analysis Portal")
st.markdown("Automated multi-agent code analysis, remediation & PR summary powered by **Groq API**.")

# Sidebar - Settings
st.sidebar.header("Settings")
api_key = st.sidebar.text_input("Groq API Key", type="password", help="Get your API key at https://console.groq.com/")
if api_key:
    os.environ["GROQ_API_KEY"] = api_key

# Knowledge Base Initialization Button
if st.sidebar.button("Index Knowledge Base (RAG)"):
    try:
        rag = KnowledgeBaseRAG()
        rag.initialize_knowledge_base()
        st.sidebar.success("Knowledge Base Indexed Successfully (Free Local Embeddings)!")
    except Exception as e:
        st.sidebar.error(f"Error indexing KB: {str(e)}")

# Session state initializations
if "last_findings" not in st.session_state:
    st.session_state.last_findings = ""
if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

tab_analysis, tab_chat = st.tabs(["🔍 Code Review & Analysis", "💬 Conversational Assistant"])

# ==================== TAB 1: CODE REVIEW & ANALYSIS ====================
with tab_analysis:
    st.header("Code Submission")
    
    submission_mode = st.radio("Submission Mode", ["Direct Code Paste", "File Upload"])

    code_content = ""
    filename = None
    if submission_mode == "Direct Code Paste":
        code_content = st.text_area("Paste Python or Java source code here...", height=250)
    else:
        uploaded_file = st.file_uploader("Upload Python or Java File", type=["py", "java"])
        if uploaded_file is not None:
            code_content = uploaded_file.getvalue().decode("utf-8")
            filename = uploaded_file.name

    if st.button("Run Code Review & Security Analysis", type="primary"):
        if not code_content.strip():
            st.warning("Please provide code input.")
        elif not os.environ.get("GROQ_API_KEY"):
            st.error("Groq API Key is missing. Please enter your API key in the sidebar.")
        else:
            submission_handler = CodeSubmissionHandler()
            val_result = submission_handler.process_submission(code_content, filename)

            if not val_result["valid"]:
                st.error(f"Syntax Validation Failed ({val_result['language']}): {val_result['message']}")
            else:
                detected_lang = val_result["language"]
                st.success(f"Language Automatically Detected: **{detected_lang}**. Executing Multi-Agent Pipeline...")

                orchestrator = MultiAgentOrchestrator()
                with st.spinner("Executing 4-agent review pipeline (Analysis, Security, Remediation, PR Summary)..."):
                    results = orchestrator.run_pipeline(code_content, detected_lang)

                results["detected_language"] = detected_lang
                st.session_state.analysis_results = results
                st.session_state.last_findings = str(results["findings"])

    # Display findings if results exist
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.divider()
        st.header("Unified Review Findings")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Detected Language", results.get("detected_language", "N/A"))
        col2.metric("Total Issues Identified", results["total_issues"])
        col3.metric("Quality / Security Split", f"{results['quality_count']} Qual / {results['security_count']} Sec")

        # Export Buttons
        col_dl1, col_dl2 = st.columns(2)
        
        # Markdown Report Generation
        md_report = f"# AI Code Review & Security Audit Report\n\n"
        md_report += f"- **Language:** {results.get('detected_language')}\n"
        md_report += f"- **Total Issues:** {results['total_issues']}\n\n"
        md_report += f"## PR Review Summary\n\n{results.get('pr_summary')}\n\n"
        md_report += "## Detailed Findings & Remediations\n\n"
        for idx, issue in enumerate(results["findings"], 1):
            md_report += f"### {idx}. [{issue.get('category')}] {issue.get('type')}\n"
            md_report += f"- **Severity:** {issue.get('severity')}\n"
            md_report += f"- **Description:** {issue.get('description')}\n\n"

        with col_dl1:
            st.download_button("📄 Download Report (.MD)", data=md_report, file_name="code_review_report.md", mime="text/markdown", use_container_width=True)

        with col_dl2:
            st.download_button("📊 Download Findings (.JSON)", data=json.dumps(results, indent=2), file_name="code_review_report.json", mime="application/json", use_container_width=True)

        st.divider()

        # PR Summary Section
        with st.expander("📝 View Pull Request (PR) Review Summary", expanded=True):
            st.markdown(results.get("pr_summary", "No PR summary generated."))

        st.subheader("Severity Scored Findings & Per-Finding Remediations")
        remediations_map = {r.get("type"): r for r in results.get("remediations", [])}

        for issue in results["findings"]:
            severity = issue.get("severity", "LOW")
            color = "🔴" if severity in ["CRITICAL", "HIGH"] else "🟡" if severity == "MEDIUM" else "🔵"
            issue_type = issue.get('type', issue.get('vulnerability', 'Issue'))

            with st.expander(f"{color} [{issue.get('category', 'Issue')}] {issue_type} - Severity: {severity}"):
                st.write(f"**Line Number:** {issue.get('line', 'N/A')}")
                st.write(f"**Description:** {issue.get('description')}")
                
                # Render matching remediation code block
                rem = remediations_map.get(issue_type)
                if rem:
                    st.markdown("---")
                    st.markdown("### 🛠️ Remediation & Refactored Fix")
                    st.write(f"**Explanation:** {rem.get('explanation')}")
                    if rem.get("corrected_code"):
                        st.code(rem.get("corrected_code"), language=results.get("detected_language", "python").lower())

# ==================== TAB 2: CONVERSATIONAL ASSISTANT ====================
with tab_chat:
    st.header("💬 Conversational Code Assistant")
    st.markdown("Ask follow-up questions about flagged issues, code smells, secure coding standards, or mitigation techniques.")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("e.g., how can i stop sql injection or fix flagged code smells?"):
        if not os.environ.get("GROQ_API_KEY"):
            st.error("Please provide your Groq API key in the sidebar first.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.spinner("Consulting secure coding knowledge base..."):
                try:
                    rag = KnowledgeBaseRAG()
                    relevant_docs = rag.query_knowledge_base(user_query, k=2)
                    context_str = "\n\n".join([doc.page_content for doc in relevant_docs])
                except Exception:
                    context_str = "No vector database context available."

            llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.2)
            
            chat_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert secure coding and code quality assistant. Answer the user's inquiry regarding code quality, code smells, or security vulnerabilities.
                
                Use the following indexed secure coding knowledge base snippets:
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
            
            if isinstance(response.content, list):
                bot_reply = "".join([part.get("text", "") if isinstance(part, dict) else str(part) for part in response.content])
            else:
                bot_reply = str(response.content)

            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            with st.chat_message("assistant"):
                st.markdown(bot_reply)
