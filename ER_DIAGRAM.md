# Database Entity Relationship (ER) Diagrams

This document contains the complete **Mermaid ER Diagrams** for all database models in the CCMS application.

The models are defined in [`backend/app/models/`](backend/app/models):
- [`Complaint`](backend/app/models/complaint.py) (`complaints` table)
- [`Chat`](backend/app/models/chat.py) (`chats` table)
- [`ChatMessage`](backend/app/models/chat.py) (`chat_messages` table)
- [`FileAttachment`](backend/app/models/file.py) (`files` table)

---

## 1. High-Level Entity Relationships

```mermaid
erDiagram
    COMPLAINT ||--o{ CHAT : "can trigger zero-or-many"
    COMPLAINT ||--o{ FILE_ATTACHMENT : "has zero-or-many"
    CHAT ||--|{ CHAT_MESSAGE : "contains one-or-many"
    CHAT ||--o{ FILE_ATTACHMENT : "attaches zero-or-many"
```

---

## 2. Detailed Database ER Diagram

```mermaid
erDiagram
    complaints {
        int id PK "Autoincrement"
        string complaint_number UK "Unique Complaint Ref ID"
        string status "NEW, IN_PROGRESS, RESOLVED, CLOSED"
        string complaint_source "Default: Pharmacy"
        string customer_name
        string customer_contact_email
        string customer_contact_phone
        string product_name
        string product_code
        string dosage_form
        string product_strength
        string batch_number
        float affected_quantity
        string affected_quantity_unit
        float normalized_quantity
        string originating_site_block
        string impacted_npm
        string complaint_category
        string title
        text description
        boolean sample_received
        string initial_severity
        string suggested_severity
        string priority
        text ai_risk_assessment
        text ai_suggested_next_action
        json ai_extra_data
        string root_cause_category
        text investigation_findings
        boolean capa_required
        text capa_details
        date incident_date
        date complaint_date
        date manufacturing_date
        date expiry_date
        date sample_received_date
        datetime investigation_start_date
        datetime investigation_completion_date
        date capa_target_date
        date capa_completion_date
        datetime resolved_date
        datetime closed_date
        datetime created_at
        datetime updated_at
    }

    chats {
        int id PK "Autoincrement"
        string title "Session Title"
        int complaint_id FK "FK -> complaints.id (SET NULL)"
        datetime created_at
        datetime updated_at
    }

    chat_messages {
        int id PK "Autoincrement"
        int chat_id FK "FK -> chats.id (CASCADE)"
        string sender "user | ai | assistant | system"
        text content
        json extra_data
        datetime created_at
    }

    files {
        int id PK "Autoincrement"
        string filename "Original file name"
        string stored_filename UK "Unique UUID/hash filename"
        string file_path "Server storage location"
        string content_type "MIME type"
        int file_size "Size in bytes"
        string extension "PDF, DOCX, TXT, EML"
        string status "PENDING, PROCESSED, FAILED"
        text extracted_text
        text processing_error
        int complaint_id FK "FK -> complaints.id (SET NULL)"
        int chat_id FK "FK -> chats.id (SET NULL)"
        datetime created_at
        datetime updated_at
    }

    complaints ||--o{ chats : "complaint_id"
    chats ||--|{ chat_messages : "chat_id"
    complaints ||--o{ files : "complaint_id"
    chats ||--o{ files : "chat_id"
```

---

## 3. Relationships & Foreign Key Rules

| Source Entity | Target Entity | Foreign Key | Cardinality | On Delete Action |
| :--- | :--- | :--- | :--- | :--- |
| `complaints` | `chats` | `chats.complaint_id` | `1 : 0..N` | `SET NULL` |
| `chats` | `chat_messages` | `chat_messages.chat_id` | `1 : 1..N` | `CASCADE` |
| `complaints` | `files` | `files.complaint_id` | `1 : 0..N` | `SET NULL` |
| `chats` | `files` | `files.chat_id` | `1 : 0..N` | `SET NULL` |
