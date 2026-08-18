# High-Level System Architecture

This document describes the 3-tier system architecture of the **AI-Powered Customer Complaint Management System (CCMS)**.

---

## 3-Tier System Architecture Diagram

```mermaid
graph TB
    subgraph PRESENTATION ["Presentation Layer (Frontend)"]
        UI[React 19 SPA]
        STORE[Redux Toolkit Store]
        FORM[Auto-Populating Log Complaint Form]
        COPILOT[AI Copilot & Risk Panel]
        COMPLETENESS[GMP Completeness Gauge]
        RCA_UI[Ishikawa 5M+E RCA Panel]
        CAPA_UI[CAPA Recommendation View]
        
        UI --- STORE
        STORE --- FORM
        STORE --- COPILOT
        STORE --- COMPLETENESS
        STORE --- RCA_UI
        STORE --- CAPA_UI
    end

    subgraph API_GATEWAY ["Application & API Gateway Layer (FastAPI Backend)"]
        FASTAPI[FastAPI Web Framework]
        
        ROUTER_CHAT[Chat APIRouter /api/v1/chats]
        ROUTER_COMPLAINT[Complaint APIRouter /api/v1/complaints]
        ROUTER_FILE[File APIRouter /api/v1/files]
        ROUTER_RCA[Root Cause Router /api/v1/root-cause]
        ROUTER_CAPA[CAPA Router /api/v1/capa-risk]
        ROUTER_DUP[Duplicate Detection Router /api/v1/duplicate-detection]
        
        FASTAPI --- ROUTER_CHAT
        FASTAPI --- ROUTER_COMPLAINT
        FASTAPI --- ROUTER_FILE
        FASTAPI --- ROUTER_RCA
        FASTAPI --- ROUTER_CAPA
        FASTAPI --- ROUTER_DUP
    end

    subgraph BUSINESS_LOGIC ["Business Logic & AI Agent Engine Layer"]
        LANGGRAPH[LangGraph StateGraph Engine]
        PYDANTIC[Pydantic v2 Schema Validation]
        PDF_LOADER[PDF & File Text Extractor]
        
        SVC_COMPLETENESS[Completeness Service]
        SVC_RCA[Root Cause Service]
        SVC_CAPA[CAPA Risk Service]
        SVC_DUP[Duplicate Detection Service]
        
        ROUTER_CHAT --> LANGGRAPH
        LANGGRAPH --> PYDANTIC
        ROUTER_FILE --> PDF_LOADER
        ROUTER_RCA --> SVC_RCA
        ROUTER_CAPA --> SVC_CAPA
        ROUTER_DUP --> SVC_DUP
        LANGGRAPH --> SVC_COMPLETENESS
    end

    subgraph INFRASTRUCTURE ["Infrastructure & External Services"]
        LLM[Groq LLM API: gemma2-9b-it / llama-3.3-70b-versatile]
        PG[(PostgreSQL Database)]
        REDIS[(Redis Cache / Job Queue)]

        LANGGRAPH -->|Async API Call| LLM
        FASTAPI -->|AsyncSQLAlchemy ORM| PG
        FASTAPI -->|Async Cache / Arq Queue| REDIS
    end

    PRESENTATION -->|REST APIs / Axios JSON| FASTAPI
```

---

## Component Architecture Overview

### 1. Presentation Layer (Frontend)
- **Framework**: React 19 + Redux Toolkit
- **Components**:
  - **Complaint Intake Form**: Dynamic form for GMP defect reporting.
  - **AI Copilot Side Panel**: Live chat, risk matrices, and follow-up email drafts.
  - **Quality Score Gauge**: Visual completeness rating (0–100%).
  - **RCA & CAPA Components**: Ishikawa 5M+E breakdown and action plans.

### 2. Application Layer (Backend)
- **Framework**: FastAPI (Python 3.12, Uvicorn)
- **ORMs & Drivers**: AsyncSQLAlchemy + Asyncpg
- **Validation**: Pydantic v2 schemas for request/response typing.

### 3. AI & Agent Layer
- **Orchestration**: LangGraph (`StateGraph`) workflow.
- **LLM Engine**: Groq Cloud API featuring ultra-low latency inference with `gemma2-9b-it` and `llama-3.3-70b-versatile`.
- **Parsing Fallbacks**: 3-level resilience pipeline ensuring complete system operation even during API key absence or rate limits.

### 4. Persistence & Infrastructure Layer
- **Database**: PostgreSQL 15+ holding `complaints`, `chats`, `chat_messages`, and `files`.
- **Caching & Queues**: Redis 6+ for async background processing and session state.

---

## Related Architecture Diagrams

- [End-to-End System Flowchart](FLOWCHART.md)
- [LangGraph Extraction Workflow](LANGGRAPH_WORKFLOW.md)
- [Database ER Diagrams](../ER_DIAGRAM.md)
