# Medical Report Upload System Design
## Post-Discharge Neurological Patient Monitoring

### System Overview

This document describes the complete medical report upload flow that gates all AI interactions in the medical chatbot system. Patients must upload their medical reports BEFORE any chatbot conversation, symptom monitoring, or risk assessment can occur.

**Principle**: Reports drive RAG knowledge → RAG guides chatbot → Chatbot gated on report status

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                             │
│  1. Patient Auth → 2. Upload Report → 3. Check Status → 4. Chat    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTP REST API
┌──────────────────────────▼──────────────────────────────────────────┐
│                      FASTAPI BACKEND                                │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Upload Endpoints                                            │  │
│  │ • POST /api/patient/{patient_id}/upload-report              │  │
│  │ • GET /api/patient/{patient_id}/report/status               │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                        │
│                           ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Report Processing Pipeline (report_upload_engine.py)       │  │
│  │                                                             │  │
│  │ 1. File Reception → 2. Text Extraction                     │  │
│  │    (PDF|Image+OCR|Plain Text)                              │  │
│  │                                                             │  │
│  │ 3. Text Cleaning → 4. Chunking                             │  │
│  │    (500 chars, 50-char overlap)                            │  │
│  │                                                             │  │
│  │ 5. Embedding Generation → 6. Vector Store                  │  │
│  │    (sentence-transformers/all-MiniLM-L6-v2)                │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                        │
│                           ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Vector Database Layer                                       │  │
│  │                                                             │  │
│  │ Shared Vector Store:                                        │  │
│  │  vector store/shared/ ← Medical books, guidelines (READ)    │  │
│  │                                                             │  │
│  │ Patient Vector Stores:                                      │  │
│  │  vector store/patient_P001/ ← Patient medical reports       │  │
│  │  vector store/patient_P002/ ← Patient medical reports       │  │
│  │  vector store/patient_PN/  ← Patient medical reports        │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                        │
│                           ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Chatbot Gating & RAG Retrieval (backend_api.py)             │  │
│  │                                                             │  │
│  │ Chat/Monitoring Endpoints Check:                            │  │
│  │ • GET /api/patient/{patient_id}/report/status               │  │
│  │ • has_medical_report = True/False                           │  │
│  │ • If False → Return BLOCKING MESSAGE                        │  │
│  │ • If True → Proceed to RAG                                  │  │
│  │                                                             │  │
│  │ Dual Vector Store Retrieval:                                │  │
│  │ • Search shared medical books store (k=3 chunks)            │  │
│  │ • Search patient-specific report store (k=3 chunks)         │  │
│  │ • Merge contexts (6 chunks max)                             │  │
│  │ • Pass to LLM                                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                        │
│                           ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Question Generation (rag_engine.py)                         │  │
│  │                                                             │  │
│  │ Input: Patient question + merged medical context           │  │
│  │ Output: Personalized monitoring question                   │  │
│  │ Knowledge: Both shared books AND patient reports           │  │
│  │ LLM: Groq mixtral-8x7b-32768                               │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                        │
│                           ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Risk Assessment (rag_engine.py)                             │  │
│  │                                                             │  │
│  │ Input: All patient symptoms + context                      │  │
│  │ Output: risk_level (LOW|MEDIUM|HIGH)                       │  │
│  │         reason (clinical rationale)                        │  │
│  │         action (recommended next step)                     │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                        │
└───────────────────────────┼────────────────────────────────────────┘
                            │ JSON Response
                            ▼
                    ┌─────────────────┐
                    │ Frontend Display│
                    │ Chat Interface  │
                    │ Risk Badge      │
                    │ Recommendations │
                    └─────────────────┘
```

---

## 1. Report Upload Endpoints

### 1.1 Upload Medical Report

**Endpoint**: `POST /api/patient/{patient_id}/upload-report`

**Request**:
```bash
curl -X POST "http://localhost:8000/api/patient/P001/upload-report" \
  -F "file=@medical_report.pdf"
```

**Supported File Types**:
- PDF files (.pdf) - Text extraction via PyPDF2
- Image files (.jpg, .jpeg, .png) - OCR via pytesseract
- Plain text (.txt) - Direct reading

**Response Success** (200 OK):
```json
{
  "success": true,
  "patient_id": "P001",
  "filename": "medical_report.pdf",
  "message": "Successfully processed PDF report: 12 chunks extracted\nCreated patient vector store with 12 chunks",
  "chunks_count": 12,
  "timestamp": "2026-01-23T10:30:45.123456"
}
```

**Response Error** (400 Bad Request):
```json
{
  "success": false,
  "patient_id": "P001",
  "filename": "invalid_file.zip",
  "message": "Text extraction failed: Unsupported file type: .zip",
  "chunks_count": 0,
  "timestamp": "2026-01-23T10:30:45.123456"
}
```

### 1.2 Check Report Status (MANDATORY FIRST CALL)

**Endpoint**: `GET /api/patient/{patient_id}/report/status`

**Purpose**: Frontend MUST call this endpoint first before allowing chat/monitoring

**Request**:
```bash
curl "http://localhost:8000/api/patient/P001/report/status"
```

**Response - With Report**:
```json
{
  "patient_id": "P001",
  "has_medical_report": true,
  "status": "Ready for monitoring",
  "can_proceed_with_monitoring": true
}
```

**Response - Without Report**:
```json
{
  "patient_id": "P001",
  "has_medical_report": false,
  "status": "Awaiting medical report upload",
  "can_proceed_with_monitoring": false
}
```

---

## 2. Report Processing Pipeline

### 2.1 File Processing Flow

**File**: `report_upload_engine.py`

#### Step 1: Text Extraction
- **PDF**: Uses PyPDF2 to extract text from all pages
- **Image**: Uses pytesseract (Tesseract OCR) to read text
- **Text**: Direct file read with UTF-8 encoding

#### Step 2: Text Cleaning
- Remove extra whitespace
- Normalize line breaks
- Filter out empty lines
- Remove special character artifacts

#### Step 3: Text Chunking
```python
CharacterTextSplitter(
    chunk_size=500,      # Optimal for embeddings
    chunk_overlap=50,    # Preserve context across chunks
    separator="\n"       # Split on line breaks first
)
```

**Example**:
- Raw text: 5000 characters
- Output: ~10 chunks of 500 chars each
- Overlap ensures symptom descriptions spanning chunk boundaries remain coherent

#### Step 4: Embedding Generation
```python
HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
```
- Creates 384-dimensional vectors for each chunk
- Enables semantic similarity search
- Runs locally (no external API calls)

#### Step 5: Vector Store Creation
```python
FAISS.from_texts(text_chunks, embeddings, metadatas=metadatas)
```
- Creates patient-specific vector store
- Path: `vector store/patient_{patient_id}/`
- Metadata includes: patient_id, chunk_index, timestamp, source_file

### 2.2 Processing Example

**Input**: Medical report PDF with discharge summary
```
Patient Name: John Smith
Discharge Date: 2026-01-15
Chief Complaint: Post-stroke monitoring
Medical History: Hypertension, Type 2 Diabetes
Current Medications: Aspirin, Metoprolol, Lisinopril
...
```

**Processing**:
1. Extract from PDF → ~2500 characters of text
2. Clean text → Remove artifacts, normalize spacing
3. Chunk → 5 chunks of ~500 chars
4. Embed → 5 vectors (384-dimensional each)
5. Store → `vector store/patient_P001/` (FAISS index)

**Chunks Created**:
- Chunk 0: Patient demographics + chief complaint
- Chunk 1: Medical history + comorbidities
- Chunk 2: Medications + dosages
- Chunk 3: Discharge instructions + warnings
- Chunk 4: Follow-up recommendations

---

## 3. Vector Database Architecture

### 3.1 Dual Vector Store Model

The system uses TWO independent vector databases:

#### A. Shared Medical Books (READ-ONLY, System-Wide)

**Path**: `vector store/shared/`

**Contents**:
- Neurology textbooks
- Clinical guidelines
- Evidence-based recommendations
- Generic medical knowledge

**Access**: ALL patients access same shared store
**Update**: System administrator only
**Use Case**: General medical context

**Example Queries**:
- "What are signs of stroke?"
- "How to manage hypertension?"
- "Post-discharge care guidelines"

#### B. Patient-Specific Medical Reports (PRIVATE, Per-Patient)

**Path**: `vector store/patient_{patient_id}/`

**Contents**:
- Patient's discharge summary
- Medications list
- Comorbidities
- Prior diagnoses
- Test results
- Imaging reports

**Access**: Only the specific patient's own data
**Update**: When patient uploads new reports
**Use Case**: Personalized monitoring context

**Example Queries for Patient P001**:
- "What medications is this patient taking?"
- "What was the patient's discharge diagnosis?"
- "What are the patient's comorbidities?"

### 3.2 Directory Structure

```
vector store/
├── shared/                          # System-wide (read-only)
│   ├── index.faiss                  # FAISS index
│   └── index.pkl                    # Metadata
├── patient_P001/                    # Patient-specific (private)
│   ├── index.faiss
│   └── index.pkl
├── patient_P002/                    # Another patient
│   ├── index.faiss
│   └── index.pkl
└── patient_PN/                      # N patients...
    ├── index.faiss
    └── index.pkl
```

### 3.3 Creation and Updates

**Initial Creation**:
- Triggered by POST /api/patient/{patient_id}/upload-report
- If vector store doesn't exist: FAISS.from_texts()
- Creates new FAISS index and saves locally

**Updates** (New Reports):
- If vector store exists: FAISS.load_local()
- Add new chunks: vector_db.add_texts()
- Save updated index: vector_db.save_local()

**Data Isolation**:
- Each patient's vector store is physically separate
- No cross-patient data leakage
- Patient can only see their own reports in retrieval

---

## 4. RAG Retrieval Logic

### 4.1 Dual-Source Retrieval

When patient asks a question:

```python
# Method: rag_engine.py - answer_question()

# 1. Retrieve from shared medical books
shared_docs = self.shared_retriever.invoke(question)  # k=3 top chunks

# 2. Retrieve from patient-specific reports
patient_docs = self.patient_retriever.invoke(question)  # k=3 top chunks

# 3. Merge contexts
merged_context = shared_docs + patient_docs  # Up to 6 chunks total

# 4. Pass to LLM
llm_prompt = format_prompt(question, merged_context)
response = call_groq_api(llm_prompt)
```

### 4.2 Retrieval Example

**Patient Question**: "Am I at risk for stroke recurrence?"

**Shared Books Retrieval** (k=3):
1. "Stroke recurrence rates range from 4-14% per year..."
2. "Risk factors for secondary stroke include hypertension, diabetes..."
3. "Post-stroke monitoring focuses on blood pressure control..."

**Patient Report Retrieval** (k=3):
1. "Past Medical History: Ischemic stroke (2023-06-15), HTN, DM2"
2. "Current Medications: Aspirin 81mg daily, Metoprolol 50mg BID"
3. "Discharge Instructions: Monitor BP daily, keep medications consistent"

**Merged Context** (6 chunks):
```
SHARED KNOWLEDGE:
Stroke recurrence rates...
Risk factors...
Monitoring approaches...

PATIENT-SPECIFIC:
This patient has history of stroke
This patient is on appropriate medications
Patient has multiple risk factors (HTN, DM)
```

**LLM Response**:
Based on shared medical knowledge + patient's specific condition, the AI generates a personalized answer:
```
"Based on your medical history and current medications, you have a 
moderate recurrence risk. Continue taking aspirin, monitor blood 
pressure daily, and maintain follow-up appointments..."
```

### 4.3 Retrieval Parameters

```python
# Number of chunks retrieved from each source
k_shared = 3     # From medical books
k_patient = 3    # From patient reports
max_total = 6    # Maximum combined chunks for LLM context

# Embedding model
model: sentence-transformers/all-MiniLM-L6-v2
dimension: 384
```

---

## 5. Chatbot Gating Logic

### 5.1 Report Status Check (MANDATORY)

Frontend must follow this flow:

```javascript
// React Frontend Flow

// STEP 1: Check report status (ALWAYS FIRST)
const statusResponse = await fetch(
  `/api/patient/${patientId}/report/status`
);
const status = await statusResponse.json();

// STEP 2: Check gating flag
if (!status.can_proceed_with_monitoring) {
  // BLOCKED - Show upload UI
  return <ReportUploadComponent />;
}

// STEP 3: Show chat UI
return <ChatComponent />;
```

### 5.2 Endpoint Gating

**Chat Endpoint**: `POST /api/chat/query`
```python
# Backend gating logic
handler = get_upload_handler()
upload_status = handler.get_upload_status(patient_id)

if not upload_status["can_proceed_with_monitoring"]:
    # BLOCK - Return error
    raise HTTPException(
        status_code=400,
        detail="Medical reports required before chatbot interaction"
    )

# ALLOW - Proceed to RAG
rag_engine = RAGEngine(patient_id)
response = rag_engine.answer_question(message)
```

**Monitoring Endpoint**: `POST /api/monitoring/session/start`
```python
# Backend gating logic (identical)
handler = get_upload_handler()
upload_status = handler.get_upload_status(patient_id)

if not upload_status["can_proceed_with_monitoring"]:
    # BLOCK - Return error
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": "NO_MEDICAL_REPORT",
            "message": "Medical reports required before monitoring"
        }
    )

# ALLOW - Create session
session_id = generate_session_id()
MONITORING_SESSIONS[session_id] = {...}
```

### 5.3 Blocking Message

When gating blocks access, return this message:

```json
{
  "error": "NO_MEDICAL_REPORT",
  "message": "Medical reports are required before symptom monitoring can begin.",
  "action": "Please upload your medical reports using the Report Upload section."
}
```

Frontend displays this message and shows upload form.

---

## 6. Question Generation with RAG Context

### 6.1 Personalized Question Generation

Input to question generator:
```
Patient Context:
- Medical history from uploaded reports
- Current medications
- Prior diagnoses
- Comorbidities

Retrieved Medical Knowledge:
- Relevant guidelines (from shared store)
- Evidence-based recommendations

Previous Answers:
- Patient's responses to prior questions
```

Output:
```
Single-line neurological symptom question:
"Have you experienced any weakness in your arms or legs?"

Answer Type: YES_NO
Explanation: "Important to monitor for recurrent stroke symptoms"
```

### 6.2 Symptom Categories Covered

Questions are based on neurological symptoms relevant to post-discharge monitoring:
- Headaches and pain patterns
- Motor function changes
- Sensory changes
- Cognitive changes
- Balance and coordination
- Sleep patterns
- Mood changes

All questions use patient's medical report for context personalization.

---

## 7. Risk Assessment Using Dual RAG

### 7.1 Risk Assessment Flow

```
Patient Symptom Responses → Merge with Dual RAG Context → LLM Assessment → Risk Level
```

**Input**:
- All patient symptom answers from monitoring session
- Merged context (shared medical books + patient reports)
- Clinical guidelines (from shared store)
- Patient's specific risk factors (from patient reports)

**LLM Task**:
```
Analyze patient symptoms against:
1. Medical knowledge (shared store)
2. Patient's specific medical history (patient store)
3. Evidence-based risk thresholds

Classify as: LOW, MEDIUM, or HIGH
```

**Output**:
```json
{
  "risk_level": "MEDIUM",
  "reason": [
    "Patient reports persistent headaches for 3 days",
    "History of migraines increases risk significance",
    "No neurological deficit symptoms reported"
  ],
  "action": "Schedule follow-up with neurologist within 1 week"
}
```

---

## 8. System Flow Diagram (Patient Journey)

```
START
 │
 ├─→ Patient Login (demo: patient1/pass123)
 │
 ├─→ [MANDATORY] Check Report Status
 │   GET /api/patient/{patient_id}/report/status
 │
 ├─→ IF has_medical_report == false:
 │   │
 │   ├─→ Show Upload UI
 │   │
 │   ├─→ Patient uploads report (PDF/Image/Text)
 │   │   POST /api/patient/{patient_id}/upload-report
 │   │
 │   ├─→ Backend processes:
 │   │   1. Extract text
 │   │   2. Clean and chunk
 │   │   3. Generate embeddings
 │   │   4. Store in patient vector DB
 │   │
 │   └─→ Re-check status
 │       GET /api/patient/{patient_id}/report/status
 │
 ├─→ IF has_medical_report == true:
 │   │
 │   ├─→ Enable Chat Interface
 │   │
 │   ├─→ Patient asks question
 │   │   POST /api/chat/query
 │   │
 │   ├─→ Backend RAG Retrieval:
 │   │   1. Search shared medical books (k=3)
 │   │   2. Search patient report store (k=3)
 │   │   3. Merge contexts
 │   │   4. Call Groq LLM
 │   │
 │   └─→ Return answer + risk level
 │
 ├─→ Patient starts symptom monitoring
 │   POST /api/monitoring/session/start
 │
 ├─→ Question loop (3-6 questions):
 │   ├─→ Get question (uses dual RAG context)
 │   │   POST /api/monitoring/session/{session_id}/next-question
 │   │
 │   ├─→ Patient answers
 │   │   POST /api/monitoring/session/{session_id}/submit-answer
 │   │
 │   └─→ Repeat until max questions reached
 │
 ├─→ Generate final risk assessment
 │   POST /api/monitoring/session/{session_id}/assessment
 │
 ├─→ Display results:
 │   - Risk Level (LOW/MEDIUM/HIGH)
 │   - Clinical Reasoning
 │   - Recommended Actions
 │
 END
```

---

## 9. Key Features & Safety Rules

### 9.1 Mandatory Preconditions

✅ **ENFORCED**:
- Medical report MUST exist before chat
- Medical report MUST exist before monitoring
- Patient vector store MUST be created before RAG retrieval
- Both shared and patient stores used for context

❌ **BLOCKED**:
- Chat without report upload
- Monitoring without report upload
- Diagnosis generation (flagged by safety rules)
- Medication recommendations

### 9.2 Data Isolation

- Patient A cannot access Patient B's medical reports
- Each patient has isolated vector store
- Shared medical books are read-only
- Vector store paths use patient_id as key

### 9.3 Quality Assurance

- Text extraction validates minimum length (50 chars)
- Chunk validation ensures meaningful content
- Embedding generation uses normalized model
- Risk levels strictly LIMITED to: LOW, MEDIUM, HIGH

---

## 10. Dependencies & Installation

### Python Packages

```bash
# Text Processing
pip install PyPDF2              # PDF extraction
pip install pytesseract         # Image OCR
pip install langchain
pip install langchain-community
pip install langchain-huggingface

# Vector Database
pip install faiss-cpu           # Local embeddings + search

# Embeddings
pip install sentence-transformers

# LLM API
pip install requests
pip install python-dotenv
```

### System Requirements

```bash
# Tesseract OCR (for image processing)
# Windows: https://github.com/UB-Mannheim/tesseract/wiki
# macOS: brew install tesseract
# Linux: apt-get install tesseract-ocr
```

---

## 11. Configuration & Environment

### .env Variables

```bash
# Required for LLM
GROQ_API_KEY=your_groq_api_key_here

# Database (if using external DB for sessions)
DATABASE_URL=sqlite:///patient_data.db
```

### Vector Store Paths

```python
# Shared medical books (system-wide)
shared_store_path = "vector store/shared/"

# Patient-specific reports
patient_store_path = f"vector store/patient_{patient_id}/"

# Upload temporary directory
upload_dir = "uploads/"

# Patient records
patient_records_dir = f"patient_records/{patient_id}/"
```

---

## 12. Troubleshooting

### Report Not Processing

**Error**: "Text extraction failed"

**Solutions**:
- Verify file format is supported (PDF/Image/TXT)
- Check file size (reasonable limits)
- For images: ensure Tesseract is installed
- For PDFs: ensure file is not encrypted

### Chatbot Still Blocked After Upload

**Error**: "Medical reports required"

**Solution**:
- Clear browser cache
- Call GET /api/patient/{patient_id}/report/status to verify
- Check vector store directory exists: `vector store/patient_{patient_id}/`

### Slow Retrieval

**Cause**: Embedding generation is CPU-intensive

**Solution**:
- First load takes ~30 seconds for model download
- Subsequent calls use cached embeddings
- Consider GPU setup for production (change device='cpu' to 'cuda')

---

## 13. Production Considerations

### Scalability

- **Vector Store**: FAISS is in-memory; consider Redis/Weaviate for distributed setup
- **Session Storage**: Current in-memory; use database in production
- **File Uploads**: Implement S3/cloud storage instead of local filesystem
- **Embedding Cache**: Pre-compute common embeddings

### Security

- Validate all file uploads (type, size, content)
- Implement rate limiting on upload endpoint
- Encrypt patient vector stores at rest
- Use proper authentication (not demo users)
- Audit log all report uploads and retrievals

### Monitoring

- Track upload success/failure rates
- Monitor RAG retrieval latency
- Alert on gating bypass attempts
- Log all AI-generated clinical assessments

---

## Summary

This system ensures that:

1. ✅ **Reports are uploaded first**: No AI interaction without reports
2. ✅ **Reports are processed efficiently**: Text → Chunks → Embeddings → Vector Store
3. ✅ **Dual RAG provides context**: Shared medical knowledge + patient-specific data
4. ✅ **Chatbot is gated**: Report status checked before every interaction
5. ✅ **Data is isolated**: Patient vectors are private and secure
6. ✅ **Questions are personalized**: Generated using patient's actual medical data
7. ✅ **Risk assessment is informed**: Uses both medical guidelines and patient context
8. ✅ **Safety is prioritized**: No diagnosis/prescription, blocking rules enforced

**The system successfully implements a RAG-based medical chatbot where patient-provided medical knowledge (uploaded reports) drives all AI clinical interactions.**
