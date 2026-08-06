# 🛡️ AI Code Review & Security Analysis Agent

An intelligent, multi-agent platform designed to automate code reviews, identify code smells, detect OWASP-standard security vulnerabilities, and provide context-aware remediation guidance using RAG (Retrieval-Augmented Generation).

---

## 📌 Project Overview

Manual code reviews are often slow, subjective, and difficult to scale, leaving critical security vulnerabilities and code quality issues undetected until late in the development lifecycle.

This project delivers an automated pipeline for **Python** and **Java** source code. When a developer submits code via direct paste or file upload, a multi-agent system orchestrates static analysis, vulnerability scanning, remediation generation, and PR summary compilation. A RAG-powered Conversational Assistant lets developers ask follow-up questions grounded in secure coding standards, and every submission is persisted to a local history store with exportable, chart-backed reports.

---

## 🏗️ System Architecture & Pipeline Flow

```text
[ Developer Submission ]
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│ Code Submission Module (Syntax Validation AST / javac)   │
└───────────────────────────┬──────────────────────────────┘
                            │ (Valid Code)
                            ▼
┌──────────────────────────────────────────────────────────┐
│        Multi-Agent Orchestrator (Parallel Execution)     │
├────────────────────────────┬─────────────────────────────┤
│   Code Analysis Agent      │   Security Vulnerability     │
│  (Code Smells & Patterns)  │   Agent (OWASP Vulns)        │
└──────────────┬─────────────┴──────────────┬──────────────┘
               │                            │
               └─────────────┬──────────────┘
                             ▼
┌──────────────────────────────────────────────────────────┐
│                     Remediation Agent                    │
│        (Generates Corrected Code & Solutions)            │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│                    PR Summary Agent                      │
│       (Compiles Structured Review & Severity Score)      │
└───────────────────────────┬──────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────┐
│     History, Reporting & RAG Assistant Layer              │
│  • Submission History (SQLite)                            │
│  • Report + Chart Generation                               │
│  • RAG Q&A grounded in ChromaDB Knowledge Base             │
└──────────────────────────────────────────────────────────┘
```

### Pipelining Process

1. **Submission & Validation** — The submission module validates syntax using language-specific tools (`ast` for Python, `javalang`/`javac` for Java). Invalid code is rejected immediately with error locations.
2. **Parallel Agent Analysis** — Validated code is processed concurrently by the **Code Analysis Agent** (design smells, complexity) and the **Security Vulnerability Agent** (OWASP vulnerabilities like SQLi, XSS, hardcoded secrets).
3. **Synthesis & Remediation** — Findings are unified and sent to the **Remediation Agent** to produce corrected code snippets. The **PR Summary Agent** consolidates everything into a structured review with a severity score.
4. **History Logging** — Each submission, along with its findings and severity score, is persisted to a local SQLite database for later retrieval and trend analysis.
5. **Reporting & Visualization** — Findings can be compiled into shareable reports, with charts summarizing vulnerability categories, severity distribution, and historical trends.
6. **Interactive RAG Q&A** — Developers can ask questions about the findings. The Conversational Assistant queries the indexed vector database (ChromaDB) to retrieve relevant secure coding guidelines before generating answers.

---

## 🎯 Milestone 1: Core Architecture & Knowledge Base Setup

Milestone 1 focused on building the foundation: system design, source code ingestion, syntax validation, and vector database indexing.

**Key Accomplishments:**
- **Knowledge Base Ingestion** — Documented OWASP guidelines and secure coding standards.
- **RAG Pipeline Construction** — Built a script to chunk, embed (via Hugging Face transformers), and index knowledge documents into a local ChromaDB vector store.
- **Syntax Validation Module** — Implemented file and paste ingestion with AST validation for Python and Java source code.
- **REST Service Endpoints** — Built initial server endpoints (`/api/submit` and `/api/chat`).

**Files Implemented:**
| File | Purpose |
|---|---|
| `build_kb.py` | Processes the knowledge base, generates vector embeddings, and builds the persistent ChromaDB store |
| `knowledge_base/owasp_guidelines.md` | OWASP Top 10 policies, secure design patterns, and anti-pattern rules |
| `main.py` | Core FastAPI service serving the submission and basic RAG chat endpoints |
| `requirements.txt` | Python package dependency registry |

---

## 🎯 Milestone 2: Multi-Agent Analysis & Orchestration Pipeline

Milestone 2 focused on agent development, parallel execution, vulnerability classification, and output aggregation.

**Key Accomplishments:**
- **Code Analysis Agent** — Detects code smells, cyclomatic complexity issues, and design anti-patterns.
- **Security Vulnerability Agent** — Scans source code for OWASP Top 10 vulnerabilities (SQL Injection, XSS, Hardcoded Secrets, IDOR).
- **Parallel Orchestrator** — Coordinates multi-agent processing using parallel thread pools, aggregating results into unified, severity-scored reports.
- **Evaluation & Testing** — Validated agent detection accuracy using sample Python and Java scripts with injected code smells and security flaws.

**Files Implemented:**
| File | Purpose |
|---|---|
| `agents/code_analysis_agent.py` | Code smell and design anti-pattern detection |
| `agents/security_agent.py` | OWASP vulnerability scanning |
| `agents/remediation_agent.py` | Generates corrected code and fix suggestions |
| `agents/pr_summary_agent.py` | Compiles the structured review and severity score |
| `tests/` | Validation and testing suite for agent accuracy |

---

## 🎯 Milestone 3: Submission History, Reporting & Streamlit UI

Milestone 3 focused on persisting review history, generating shareable reports with visual analytics, and wrapping the pipeline in an interactive web interface.

**Key Accomplishments:**
- **Submission History Tracking** — Every code submission, its findings, and its severity score are stored in a local SQLite database, allowing developers to revisit past reviews.
- **Report Generation** — Structured, human-readable reports are compiled from agent findings for sharing or archiving (e.g., as part of a PR).
- **Chart & Visualization Support** — Vulnerability categories, severity breakdowns, and historical trends are rendered as charts to make findings easier to interpret at a glance.
- **Streamlit Web UI** — The pipeline is exposed through an interactive Streamlit app, replacing/augmenting the raw REST endpoints from Milestone 1.

**Files Implemented:**
| File | Purpose |
|---|---|
| `src/history_manager.py` | Reads/writes submission history to `submission_history.db` (SQLite) |
| `src/report_generator.py` | Compiles agent findings into structured reports |
| `src/charts.py` | Generates charts/visualizations (severity distribution, category breakdown, trends) |
| `app.py` | Streamlit Web UI tying submission, analysis, history, and reporting together |
| `submission_history.db` | Auto-generated SQLite database storing past submissions |

---

## 📁 Project Structure

```text
.
├── .env                        # Optional environment variables (API keys, config)
├── README.md                   # Project setup, requirements, and execution instructions
├── requirements.txt            # Python dependencies
├── app.py                      # Streamlit Web UI
├── submission_history.db       # Auto-generated SQLite DB storing past submissions
├── knowledge_base/             # Knowledge base folder for the RAG pipeline
│   └── owasp_guidelines.md     # OWASP standards & secure coding guidelines document
├── chroma_db/                  # Auto-generated vector database store
├── src/                        # Main application source code
│   ├── history_manager.py      # Submission history persistence (SQLite)
│   ├── report_generator.py     # Report compilation from agent findings
│   └── charts.py                # Chart/visualization generation
├── agents/                     # Specialized multi-agent modules
│   ├── code_analysis_agent.py  # Code smell & design anti-pattern detection
│   ├── security_agent.py       # OWASP vulnerability scanning
│   ├── remediation_agent.py    # Corrected code / remediation generation
│   └── pr_summary_agent.py     # Structured review & severity scoring
└── tests/                      # Validation & testing codebases
```

---

## 🤖 Multi-Agent Modules

| Agent | Responsibility |
|---|---|
| **Code Analysis Agent** | Detects code smells, high cyclomatic complexity, and design anti-patterns |
| **Security Agent** | Scans for OWASP Top 10 vulnerabilities (SQL Injection, XSS, hardcoded secrets, IDOR, etc.) |
| **Remediation Agent** | Produces corrected code snippets and fix guidance for identified issues |
| **PR Summary Agent** | Consolidates all findings into a structured, severity-scored review |

---

## ⚙️ Prerequisites

- **Python**: 3.10+
- **Java Development Kit (JDK)**: `javac` installed and configured in the system path
- **Hugging Face Account & API Token**: Required for free embedding and model access

---

## 🚀 Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
