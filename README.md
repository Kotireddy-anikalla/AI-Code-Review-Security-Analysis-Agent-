#🛡️ AI Code Review & Security Analysis Agent
An intelligent, multi-agent platform designed to automate code reviews, identify code smells, detect OWASP-standard security vulnerabilities, and provide context-aware remediation guidance using RAG (Retrieval-Augmented Generation).
## Project Overview
 Manual code reviews are often slow, subjective, and difficult to scale, leaving critical security vulnerabilities and code quality issues undetected until late in the development lifecycle.  This project delivers an automated pipeline for Python and Java source code. When a developer submits code via direct paste or file upload , a multi-agent system orchestrates static analysis, vulnerability scanning, remediation generation, and PR summary compilation. Additionally, a RAG-powered Conversational Assistant enables developers to ask follow-up questions grounded in secure coding standards. 
##System Architecture & Pipeline Flow
The platform relies on a modular, multi-agent pipeline:
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
│   Code Analysis Agent      │ Security Vulnerability Agent│
│  (Code Smells & Patterns)  │    (OWASP Vulnerabilities)  │
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
│        RAG Conversational Assistant (Q&A Interface)      │
│         (Grounded in ChromaDB Knowledge Base)            │
└──────────────────────────────────────────────────────────┘

## Pipelining Process
Submission & Validation: The submission module validates syntax using language-specific tools (ast for Python, javalang/javac for Java). Invalid code is rejected immediately with error locations.  
Parallel Agent Analysis: Validated code is processed concurrently by the Code Analysis Agent (design smells, complexity) and the Security Vulnerability Agent (OWASP vulnerabilities like SQLi, XSS, hardcoded secrets). 
Synthesis & Remediation: Findings are unified and sent to the Remediation Agent to produce corrected code snippets. The PR Summary Agent consolidates everything into a structured review.  
Interactive RAG Q&A: Developers can ask questions regarding the findings. The Conversational Assistant queries the indexed vector database (ChromaDB) to retrieve relevant secure coding guidelines before generating answers. 

## Milestone 1: Core Architecture & Knowledge Base 
SetupMilestone 1 focuses on building the foundation: system design, source code ingestion, syntax validation, and vector database indexing.  
#Key Accomplishments:
Knowledge Base Ingestion: Documented OWASP guidelines and secure coding standards into knowledge.txt.  
RAG Pipeline Construction: Built build_kb.py to chunk, embed (via Hugging Face transformers), and index knowledge documents into a local ChromaDB vector store.
Syntax Validation Module: Implemented file and paste ingestion with AST validation for Python and Java source code.  
REST Service Endpoints: Built initial server endpoints (/api/submit and /api/chat) inside 
##Files Implemented (Milestone 1):
build_kb.py: Script to process knowledge.txt, generate vector embeddings, and build the persistent ChromaDB store.
knowledge.txt: Knowledge base containing OWASP Top 10 policies, secure design patterns, and anti-pattern rules.  
main.py: Core FastAPI service serving the submission and basic RAG chat endpoints.
requirements.txt: Python package dependency registry.
##Milestone 2: Multi-Agent Analysis & Orchestration Pipeline
Milestone 2 focuses on agent development, parallel execution, vulnerability classification, and output aggregation
##Key Accomplishments:
Code Analysis Agent: Detects code smells, cyclomatic complexity issues, and design anti-patterns.  
Security Vulnerability Agent: Scans source code for OWASP Top 10 vulnerabilities (SQL Injection, XSS, Hardcoded Secrets, IDOR).  
Parallel Orchestrator: Coordinates multi-agent processing using parallel thread pools, aggregating results into unified severity-scored reports.  
Evaluation & Testing: Validated agent detection accuracy using sample Python and Java scripts with injected code smells and security flaws
Prerequisites & Installation
##Prerequisites
Python: 3.10+

Java Development Kit (JDK): javac installed and configured in system path

Hugging Face Account & API Token: Required for free embedding and model access
