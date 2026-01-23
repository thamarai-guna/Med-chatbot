# FastAPI Backend - Complete API Reference & Testing Guide

## OVERVIEW

This document maps the existing Streamlit chatbot features to FastAPI REST endpoints.

### Key Principles
- ✅ **Same AI behavior** - Uses exact same RAG logic from rag_engine.py
- ✅ **Same risk logic** - Uses exact same risk assessment from _assess_medical_risk()
- ✅ **Reuses all code** - Imports existing modules (rag_engine, patient_manager, falcon)
- ✅ **JSON responses** - All endpoints return JSON
- ✅ **No UI dependencies** - Zero Streamlit imports

---

## RUNNING THE API

### 1. Install dependencies
```bash
pip install -r requirements_backend.txt
```

### 2. Start FastAPI server
```bash
# Option A: Direct Python
python backend_api.py

# Option B: Uvicorn (recommended)
uvicorn backend_api:app --reload --host 0.0.0.0 --port 8000

# Option C: With logging
uvicorn backend_api:app --reload --host 127.0.0.1 --port 8000 --log-level debug
```

### 3. Access the API
- **Swagger UI (interactive):** http://localhost:8000/docs
- **ReDoc (documentation):** http://localhost:8000/redoc
- **JSON Schema:** http://localhost:8000/openapi.json

---

## STREAMLIT → FASTAPI MAPPING

### Patient Management

| Feature | Streamlit | FastAPI Endpoint |
|---------|-----------|------------------|
| Register Patient | Sidebar form | `POST /api/patient/register` |
| Select Patient | Dropdown | `GET /api/patient/{patient_id}` |
| List All Patients | Admin view | `GET /api/patient` |
| View Risk Summary | Dashboard widget | `GET /api/patient/{patient_id}/risk/summary` |

### Chat Features

| Feature | Streamlit | FastAPI Endpoint |
|---------|-----------|------------------|
| Send message | Chat input | `POST /api/chat/query` |
| View chat history | History tab | `GET /api/chat/history/{patient_id}` |
| Clear history | Delete button | `DELETE /api/chat/history/{patient_id}` |

### Documents

| Feature | Streamlit | FastAPI Endpoint |
|---------|-----------|------------------|
| Upload PDFs/TXT | File uploader | `POST /api/documents/upload` |
| Create vector store | Form submit | (same endpoint) |

---

## API ENDPOINTS - DETAILED

### 1. HEALTH CHECK

**Endpoint:** `GET /health`

**Purpose:** Verify API is running

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-23T10:30:45.123456",
  "version": "1.0.0"
}
```

**curl:**
```bash
curl http://localhost:8000/health
```

---

### 2. PATIENT REGISTRATION

**Endpoint:** `POST /api/patient/register`

**Purpose:** Register a new patient

**Request:**
```json
{
  "patient_id": "P001",
  "name": "John Doe",
  "email": "john@hospital.com",
  "age": 45,
  "medical_history": "Diabetes Type 2, Hypertension"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Patient John Doe registered successfully",
  "patient_id": "P001"
}
```

**Response (Error - Duplicate):**
```json
{
  "error": true,
  "message": "Patient ID or email already exists",
  "timestamp": "2026-01-23T10:30:45.123456"
}
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/patient/register \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "name": "John Doe",
    "email": "john@hospital.com",
    "age": 45,
    "medical_history": "Diabetes Type 2"
  }'
```

**Postman:**
- Method: POST
- URL: http://localhost:8000/api/patient/register
- Body (JSON):
```json
{
  "patient_id": "P001",
  "name": "John Doe",
  "email": "john@hospital.com",
  "age": 45,
  "medical_history": "Diabetes Type 2, Hypertension"
}
```

---

### 3. GET PATIENT INFO

**Endpoint:** `GET /api/patient/{patient_id}`

**Purpose:** Get patient details

**Response:**
```json
{
  "patient_id": "P001",
  "name": "John Doe",
  "email": "john@hospital.com",
  "age": 45,
  "medical_history": "Diabetes Type 2, Hypertension",
  "created_at": "2026-01-23T10:30:45.123456",
  "last_accessed": "2026-01-23T10:35:20.654321"
}
```

**curl:**
```bash
curl http://localhost:8000/api/patient/P001
```

---

### 4. LIST ALL PATIENTS

**Endpoint:** `GET /api/patient`

**Purpose:** Get all registered patients (admin use)

**Response:**
```json
{
  "total": 2,
  "patients": [
    {
      "patient_id": "P001",
      "name": "John Doe",
      "email": "john@hospital.com",
      "age": 45,
      "created_at": "2026-01-23T10:30:45.123456"
    },
    {
      "patient_id": "P002",
      "name": "Jane Smith",
      "email": "jane@hospital.com",
      "age": 38,
      "created_at": "2026-01-23T10:35:20.654321"
    }
  ]
}
```

**curl:**
```bash
curl http://localhost:8000/api/patient
```

---

### 5. CHAT QUERY (MAIN ENDPOINT)

**Endpoint:** `POST /api/chat/query`

**Purpose:** Ask a medical question (same as Streamlit chat)

**Request:**
```json
{
  "patient_id": "P001",
  "message": "What are the symptoms of cardiac arrhythmia?",
  "vector_store_name": "DefaultVectorDB"
}
```

**Response:**
```json
{
  "patient_id": "P001",
  "question": "What are the symptoms of cardiac arrhythmia?",
  "answer": "Cardiac arrhythmia can present with...",
  "risk_level": "MEDIUM",
  "risk_reason": "Patient inquiring about cardiac symptoms which warrant medical evaluation.",
  "source_documents": [
    "Arrhythmia occurs when the electrical system...",
    "Common symptoms include palpitations, chest pain..."
  ],
  "timestamp": "2026-01-23T10:40:15.123456"
}
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "message": "What are the symptoms of cardiac arrhythmia?",
    "vector_store_name": "DefaultVectorDB"
  }'
```

**Note:** This endpoint:
- ✅ Uses exact same RAG logic as Streamlit
- ✅ Returns same AI response
- ✅ Performs same risk assessment
- ✅ Saves to patient history automatically
- ✅ Retrieves documents from FAISS

---

### 6. GET CHAT HISTORY

**Endpoint:** `GET /api/chat/history/{patient_id}?limit=50`

**Purpose:** Retrieve patient's chat history

**Query Parameters:**
- `limit` (optional): Max records to return (default: 50)

**Response:**
```json
{
  "patient_id": "P001",
  "total": 3,
  "history": [
    {
      "id": 0,
      "question": "What is diabetes?",
      "answer": "Diabetes is a metabolic disorder...",
      "risk_level": "LOW",
      "risk_reason": "General health information query",
      "source_documents": ["...", "..."],
      "timestamp": "2026-01-23T10:20:00.123456"
    },
    {
      "id": 1,
      "question": "I have chest pain",
      "answer": "Chest pain requires immediate medical attention...",
      "risk_level": "HIGH",
      "risk_reason": "Patient reporting acute chest pain symptoms",
      "source_documents": ["...", "..."],
      "timestamp": "2026-01-23T10:25:00.123456"
    }
  ]
}
```

**curl:**
```bash
# Get last 20 messages
curl 'http://localhost:8000/api/chat/history/P001?limit=20'

# Get all history
curl 'http://localhost:8000/api/chat/history/P001'
```

---

### 7. CLEAR CHAT HISTORY

**Endpoint:** `DELETE /api/chat/history/{patient_id}`

**Purpose:** Delete all chat history (GDPR right to be forgotten)

**Response:**
```json
{
  "success": true,
  "message": "Chat history cleared for patient P001"
}
```

**curl:**
```bash
curl -X DELETE http://localhost:8000/api/chat/history/P001
```

---

### 8. GET RISK SUMMARY

**Endpoint:** `GET /api/patient/{patient_id}/risk/summary?days=30`

**Purpose:** Get risk assessment summary

**Query Parameters:**
- `days` (optional): Look-back period (default: 30)

**Response:**
```json
{
  "patient_id": "P001",
  "total_queries": 10,
  "max_risk_level": "HIGH",
  "risk_distribution": {
    "CRITICAL": 0,
    "HIGH": 2,
    "MEDIUM": 3,
    "LOW": 5,
    "UNKNOWN": 0
  }
}
```

**curl:**
```bash
# Last 30 days
curl 'http://localhost:8000/api/patient/P001/risk/summary'

# Last 7 days
curl 'http://localhost:8000/api/patient/P001/risk/summary?days=7'
```

---

### 9. UPLOAD DOCUMENTS

**Endpoint:** `POST /api/documents/upload`

**Purpose:** Upload and process medical documents

**Parameters:**
- `files` (required): PDF/TXT files
- `chunk_size` (optional): Default 512
- `chunk_overlap` (optional): Default 50
- `vector_store_name` (optional): Default "DefaultVectorDB"
- `merge_with_existing` (optional): Default false

**Response:**
```json
{
  "success": true,
  "message": "Processed 2 file(s)",
  "chunks_created": 145,
  "vector_store": "DefaultVectorDB",
  "timestamp": "2026-01-23T10:45:30.123456"
}
```

**curl:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "files=@medical_document.pdf" \
  -F "files=@another_document.txt" \
  -F "chunk_size=512" \
  -F "chunk_overlap=50" \
  -F "vector_store_name=DefaultVectorDB"
```

**Postman:**
- Method: POST
- URL: http://localhost:8000/api/documents/upload
- Body: form-data
  - `files`: Select PDF/TXT files (multiple)
  - `vector_store_name`: DefaultVectorDB
  - `chunk_size`: 512
  - `chunk_overlap`: 50

---

## COMPLETE WORKFLOW EXAMPLE

### Scenario: Create patient → Upload docs → Chat → Get history

**Step 1: Register Patient**
```bash
curl -X POST http://localhost:8000/api/patient/register \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "name": "Alice Smith",
    "age": 52
  }'
```

**Step 2: Upload Medical Documents**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "files=@cardiology_guide.pdf" \
  -F "vector_store_name=DefaultVectorDB"
```

**Step 3: Chat with Patient (Same as Streamlit)**
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "message": "I have palpitations. Is this serious?",
    "vector_store_name": "DefaultVectorDB"
  }'
```

**Response (from Groq LLM):**
```json
{
  "patient_id": "P001",
  "question": "I have palpitations. Is this serious?",
  "answer": "Palpitations can indicate various cardiac conditions... [full medical response from Groq]",
  "risk_level": "MEDIUM",
  "risk_reason": "Patient reporting cardiac symptoms (palpitations) requiring medical evaluation",
  "source_documents": ["Palpitations are sensations of heartbeat...", "..."],
  "timestamp": "2026-01-23T10:50:00.123456"
}
```

**Step 4: View Chat History**
```bash
curl 'http://localhost:8000/api/chat/history/P001'
```

**Step 5: Check Risk Summary**
```bash
curl 'http://localhost:8000/api/patient/P001/risk/summary'
```

---

## VERIFICATION: Streamlit vs FastAPI Output

### How to verify they produce same results

**A. Chat Query Comparison**

1. **In Streamlit:**
   - Register Patient: "TEST_P001"
   - Ask: "What is hypertension?"
   - Note the answer, risk level, source docs

2. **Via FastAPI:**
   ```bash
   # Register (FastAPI)
   curl -X POST http://localhost:8000/api/patient/register \
     -H "Content-Type: application/json" \
     -d '{"patient_id": "TEST_P001", "name": "Test", "age": 45}'
   
   # Chat (FastAPI)
   curl -X POST http://localhost:8000/api/chat/query \
     -H "Content-Type: application/json" \
     -d '{"patient_id": "TEST_P001", "message": "What is hypertension?"}'
   ```

3. **Compare:**
   - ✅ Should get identical answer from Groq
   - ✅ Should get identical risk_level
   - ✅ Should get identical source documents
   - ✅ Should show up in both histories

**B. Database Verification**

Both Streamlit and FastAPI use the SAME SQLite database:
- Location: `patient_data.db`
- Tables: `patients`, `chat_history`, `risk_assessments`

If you chat in Streamlit, history appears in FastAPI (and vice versa).

---

## ERROR RESPONSES

### 404 - Patient Not Found
```json
{
  "error": true,
  "message": "Patient P999 not found",
  "timestamp": "2026-01-23T10:50:00.123456"
}
```

### 400 - Bad Request
```json
{
  "error": true,
  "message": "No files provided",
  "timestamp": "2026-01-23T10:50:00.123456"
}
```

### 500 - Server Error
```json
{
  "error": true,
  "message": "Internal server error",
  "detail": "[actual error details]",
  "timestamp": "2026-01-23T10:50:00.123456"
}
```

---

## TESTING CHECKLIST

- [ ] Run FastAPI server successfully
- [ ] POST /api/patient/register works
- [ ] GET /api/patient/{patient_id} works
- [ ] POST /api/chat/query returns same output as Streamlit
- [ ] GET /api/chat/history shows all messages
- [ ] DELETE /api/chat/history clears history
- [ ] GET /api/patient/{patient_id}/risk/summary shows correct stats
- [ ] POST /api/documents/upload processes files
- [ ] Data persists in SQLite (check patient_data.db)
- [ ] FastAPI and Streamlit share the same database
- [ ] Swagger UI at /docs shows all endpoints
- [ ] All error responses are proper JSON

---

## IMPORTANT NOTES

### Code Reuse
- ✅ Uses existing `rag_engine.RAGEngine` class
- ✅ Uses existing `patient_manager.PatientManager`
- ✅ Uses existing `falcon.py` for document processing
- ✅ NO changes to AI logic, prompts, or models
- ✅ NO Streamlit imports in backend_api.py

### Database
- Both Streamlit and FastAPI use the SAME `patient_data.db`
- Changes in one are immediately visible in the other
- This enables gradual migration from Streamlit to React+FastAPI

### Streamlit Status
- Streamlit app remains untouched
- Acts as reference implementation
- Can run simultaneously with FastAPI (on different ports)
- Will be replaced by React frontend in next phase

---

## NEXT STEPS (Not yet implemented)

- React frontend to replace Streamlit UI
- Authentication & authorization layer
- Doctor/nurse/patient role-based views
- Edge device alert ingestion APIs
- Database migration to PostgreSQL
