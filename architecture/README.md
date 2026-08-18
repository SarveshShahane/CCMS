# CCMS Architecture & Technical Diagrams

This directory contains the formal system architecture, data flow diagrams, and component specifications for the **AI-Powered Customer Complaint Management System (CCMS)**.

---

## Architecture Documents & Diagrams

| Document | Description | Primary Diagram Type |
| :--- | :--- | :--- |
| **[End-to-End Flowchart](FLOWCHART.md)** | Complete processing flowchart from raw user input / document upload down to PostgreSQL storage. | `Mermaid flowchart TD` |
| **[High-Level System Architecture](SYSTEM_ARCHITECTURE.md)** | 3-tier architecture breakdown (Presentation, API Gateway, AI Agent Services, Infrastructure). | `Mermaid graph TB` |
| **[LangGraph Extraction Workflow](LANGGRAPH_WORKFLOW.md)** | State machine and 3-tier fallback execution chain for Groq LLM extraction. | `Mermaid stateDiagram-v2` & `flowchart LR` |
| **[Database ER Diagrams](../ER_DIAGRAM.md)** | Full entity-relationship diagrams, database schemas, data types, and foreign key rules. | `Mermaid erDiagram` |

---

## Quick Navigation

```
CCMS Architecture Index/
├── FLOWCHART.md                # 1. End-to-End Processing Flowchart (User -> File/Text -> DB)
├── SYSTEM_ARCHITECTURE.md      # 2. 3-Tier System Architecture Diagram
├── LANGGRAPH_WORKFLOW.md       # 3. LangGraph State Machine & Fallback Hierarchy
└── ../ER_DIAGRAM.md            # 4. Database Entity-Relationship Diagrams
```
