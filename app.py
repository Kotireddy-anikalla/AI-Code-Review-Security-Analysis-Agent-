import streamlit as st
import os
import uuid
from src.submission import CodeSubmissionHandler
from src.orchestration import MultiAgentOrchestrator
from src.rag_pipeline import KnowledgeBaseRAG
from src.history_manager import HistoryManager
from src.report_generator import generate_pdf_report
from src.charts import build_severity_pie_chart, build_category_bar_chart, build_severity_by_category_chart
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
if "current_submission_id" not in st.session_state:
    st.session_state.current_submission_id = None
if "current_project_name" not in st.session_state:
    st.session_state.current_project_name = None
if "pdf_report_bytes" not in st.session_state:
    st.session_state.pdf_report_bytes = None

history_manager = HistoryManager()

tab_analysis, tab_chat, tab_history = st.tabs(
    ["🔍 Code Review & Analysis", "💬 Conversational Assistant", "🕑 Submission History"]
)

# ==================== TAB 1: CODE REVIEW & ANALYSIS ====================
with tab_analysis:
    st.header("Code Submission")

    project_name = st.text_input("Project Name", value="Untitled Project")
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

                submission_id = uuid.uuid4().hex[:8]
                st.session_state.analysis_results = results
                st.session_state.last_findings = str(results["findings"])
                st.session_state.current_submission_id = submission_id
                st.session_state.current_project_name = project_name

                # Persist to submission history so it's browsable in the History tab.
                history_manager.save_submission(
                    submission_id=submission_id,
                    project_name=project_name,
                    language=detected_lang,
                    code=code_content,
                    results=results,
                )

                # Pre-build the PDF once here rather than regenerating it on every rerun.
                st.session_state.pdf_report_bytes = generate_pdf_report(
                    submission_id, project_name, detected_lang, results
                ).getvalue()

    # Display findings if results exist
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results

        st.divider()
        st.header("Unified Review Findings")

        st.caption(
            f"**Submission ID:** `{st.session_state.current_submission_id}`  |  "
            f"**Project:** {st.session_state.current_project_name}  |  "
            f"**Language:** {results.get('detected_language', 'N/A')}"
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Detected Language", results.get("detected_language", "N/A"))
        col2.metric("Total Issues Identified", results["total_issues"])
        col3.metric("Quality / Security Split", f"{results['quality_count']} Qual / {results['security_count']} Sec")

        # Graphical presentation of findings
        st.subheader("📊 Visual Overview")
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.plotly_chart(build_severity_pie_chart(results["findings"]), use_container_width=True)
        with chart_col2:
            st.plotly_chart(
                build_category_bar_chart(results["quality_count"], results["security_count"]),
                use_container_width=True,
            )
        st.plotly_chart(build_severity_by_category_chart(results["findings"]), use_container_width=True)

        # Export: PDF report only
        if st.session_state.pdf_report_bytes:
            st.download_button(
                "📄 Download Full Report (.PDF)",
                data=st.session_state.pdf_report_bytes,
                file_name=f"{st.session_state.current_project_name}_code_review_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

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

# ==================== TAB 3: SUBMISSION HISTORY ====================
with tab_history:
    st.header("🕑 Previous Submissions")
    st.markdown("Every completed review is saved automatically. Reload a past submission below to view its full findings, charts, and PDF report again.")

    submissions = history_manager.list_submissions()

    if not submissions:
        st.info("No previous submissions yet. Run a review in the **Code Review & Analysis** tab to build history.")
    else:
        for sub in submissions:
            label = f"{sub['project_name']} — {sub['language']} — {sub['created_at']} (ID: {sub['submission_id']})"
            with st.expander(label):
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Total Issues", sub["total_issues"])
                col_b.metric("Quality Issues", sub["quality_count"])
                col_c.metric("Security Issues", sub["security_count"])

                col_load, col_delete = st.columns(2)
                if col_load.button("📂 Load Into Review Tab", key=f"view_{sub['submission_id']}", use_container_width=True):
                    record = history_manager.get_submission(sub["submission_id"])
                    loaded_results = record["results"]
                    loaded_results["detected_language"] = record["language"]

                    st.session_state.analysis_results = loaded_results
                    st.session_state.last_findings = str(loaded_results.get("findings", ""))
                    st.session_state.current_submission_id = record["submission_id"]
                    st.session_state.current_project_name = record["project_name"]
                    st.session_state.pdf_report_bytes = generate_pdf_report(
                        record["submission_id"], record["project_name"], record["language"], loaded_results
                    ).getvalue()

                    st.success("Loaded — switch to the **Code Review & Analysis** tab to view it.")

                if col_delete.button("🗑️ Delete", key=f"del_{sub['submission_id']}", use_container_width=True):
                    history_manager.delete_submission(sub["submission_id"])
                    st.rerun()
