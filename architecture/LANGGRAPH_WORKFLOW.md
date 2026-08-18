# LangGraph Agent Workflow & Fallback Chain

This document details the internal **LangGraph `StateGraph` workflow** responsible for structured complaint extraction, schema validation, and fallback handling.

---

## LangGraph State Machine Diagram

```mermaid
stateDiagram-v2
    [*] --> START
    
    state START {
        [*] --> InitState : Load user_input & LLMConfig
    }

    InitState --> ExtractNode : Pass ComplaintState to extract_complaint_node

    state ExtractNode {
        [*] --> CheckLLM : Validate LLM API Key
        
        CheckLLM --> LLM_Primary : API Key Present
        CheckLLM --> Fallback_Parser : API Key Missing
        
        LLM_Primary --> Output_Validation : Run ChatPromptTemplate + PydanticOutputParser
        Output_Validation --> Success : JSON Parse Succeeded
        Output_Validation --> LLM_Structured_Fallback : JSON Parse Error / Exception
        
        LLM_Structured_Fallback --> Success : Structured Output Succeeded
        LLM_Structured_Fallback --> Fallback_Parser : Exception / Failed
        
        Fallback_Parser --> Regex_Keyword_Extraction : Execute Deterministic Fallback
        Regex_Keyword_Extraction --> Success : Return ComplaintExtractionOutput
    }

    Success --> CompletenessEnricher : Compute Completeness Score & Missing Fields
    CompletenessEnricher --> END

    END --> [*]
```

---

## State Definition (`ComplaintState`)

The state object maintained across node transitions:

```python
class ComplaintState(TypedDict):
    user_input: str
    llm_config: Optional[LLMConfig]
    extracted_output: Optional[ComplaintExtractionOutput]
    error: Optional[str]
```

---

## Resilience & Fallback Hierarchy

```mermaid
flowchart LR
    A[Raw Complaint Input] --> B[Level 1: Groq LLM + Pydantic JSON Prompt]
    B -->|Success| E[Valid ComplaintExtractionOutput]
    B -->|Failure / Invalid JSON| C[Level 2: Groq LLM .with_structured_output]
    C -->|Success| E
    C -->|Failure / LLM Offline| D[Level 3: Regex & Keyword Fallback Engine]
    D --> E
```

---

## Related Architecture Diagrams

- [End-to-End System Flowchart](FLOWCHART.md)
- [High-Level System Architecture](SYSTEM_ARCHITECTURE.md)
- [Database ER Diagrams](../ER_DIAGRAM.md)
