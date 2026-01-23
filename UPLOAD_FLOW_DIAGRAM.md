# Medical Report Upload Flow - Visual Guide

## Complete System Flow Diagram

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                                                           │
│                    MEDICAL REPORT UPLOAD SYSTEM                          │
│                                                                           │
│                      POST-DISCHARGE NEUROLOGICAL MONITORING               │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: PATIENT LOGIN & GATING CHECK
═══════════════════════════════════════════════════════════════════════════════

    Frontend                         Backend API                   Database
       │                                │                             │
       │ 1. Patient Login               │                             │
       │─────────────────→ POST /auth/login ────→ Validate ──→ Patient DB
       │                                │                             │
       │← Access Token ──────────────────│                             │
       │                                │                             │
       │ 2. Check Report Status         │                             │
       │─────────────────→ GET /report/status ──→ Check ───────────→ Vector
       │                                │         vector store        Store
       │← {has_medical_report: ?} ──────│                             │
       │                                │                             │

    Decision Point:
    ┌─────────────────────────────────────────────────────────────┐
    │ if has_medical_report == FALSE:                             │
    │   ├─→ BLOCK chat, monitoring, analysis                      │
    │   └─→ SHOW Report Upload UI                                 │
    │ else (TRUE):                                                │
    │   ├─→ ENABLE chat interface                                 │
    │   ├─→ ENABLE symptom monitoring                             │
    │   └─→ ENABLE risk assessment                                │
    └─────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════
PHASE 2: MEDICAL REPORT UPLOAD & PROCESSING
═══════════════════════════════════════════════════════════════════════════════

    Frontend                    Backend API                 Processing
       │                            │                           │
       │ 3. Upload Report File     │                            │
       │─────────────────→ POST /upload-report ────────────────→│
       │                            │                           │
       │                            │                        ┌──┴─────────┐
       │                            │                        │Processing  │
       │                            │                        │Pipeline    │
       │                            │                        │            │
       │                            │                        │ STEP 1:    │
       │                            │                        │ Extract    │
       │                            │                        │ Text       │
       │                            │                        │ ┌────────┐ │
       │                            │                        │ │ PDF    │ │
       │                            │                        │ │ Image  │ │─→ Raw Text
       │                            │                        │ │ Text   │ │
       │                            │                        │ └────────┘ │
       │                            │                        │            │
       │                            │                        │ STEP 2:    │
       │                            │                        │ Clean      │
       │                            │                        │ Text       │
       │                            │                        │ ┌────────┐ │
       │                            │                        │ │Remove  │ │
       │                            │                        │ │Artifacts  │─→ Clean Text
       │                            │                        │ │Normalize  │
       │                            │                        │ └────────┘ │
       │                            │                        │            │
       │                            │                        │ STEP 3:    │
       │                            │                        │ Chunk      │
       │                            │                        │ Text       │
       │                            │                        │ ┌────────┐ │
       │                            │                        │ │500 chr │ │
       │                            │                        │ │overlap │─→ Text Chunks
       │                            │                        │ │50 chr  │ │
       │                            │                        │ └────────┘ │
       │                            │                        │            │
       │                            │                        │ STEP 4:    │
       │                            │                        │ Embed      │
       │                            │                        │ ┌────────┐ │
       │                            │                        │ │sentence│ │
       │                            │                        │ │transfor│─→ Vectors
       │                            │                        │ │s384dim │ │
       │                            │                        │ └────────┘ │
       │                            │                        │            │
       │                            │                        │ STEP 5:    │
       │                            │                        │ Store      │
       │                            │                        │ ┌────────┐ │
       │                            │                        │ │FAISS   │ │
       │                            │                        │ │Index   │─→ Vector DB
       │                            │                        │ └────────┘ │
       │                            │                        │            │
       │                            │← {success: true} ──────│            │
       │                            │   chunks_count: N     │            │
       │                            │   message: "..."      │            │
       │                            │                       └────────────┘
       │← Upload Complete ──────────│
       │   Show Success Message     │
       │                            │


═══════════════════════════════════════════════════════════════════════════════
PHASE 3: VECTOR DATABASE STATE
═══════════════════════════════════════════════════════════════════════════════

    After successful upload:

    Filesystem                          Memory (FAISS Indices)
    ──────────────────────────────────────────────────────────

    vector store/
    ├── shared/                         Shared Medical Books
    │   ├── index.faiss    ──→──────→  (384-dim, k=3 retrieval)
    │   └── index.pkl                   • Guidelines
    │                                   • Evidence-based knowledge
    │                                   • Generic medical context
    │
    └── patient_P001/                   Patient-Specific Reports
        ├── index.faiss    ──→──────→  (384-dim, k=3 retrieval)
        └── index.pkl                   • P001's medical history
                                        • P001's medications
                                        • P001's diagnoses
                                        • P001's discharge data


═══════════════════════════════════════════════════════════════════════════════
PHASE 4: CHATBOT ACTIVATION - DUAL RAG RETRIEVAL
═══════════════════════════════════════════════════════════════════════════════

    Frontend                       Backend API                 Vector Stores
       │                               │                            │
       │ 4. Ask Question              │                            │
       │─────────────────→ POST /chat/query ──────────────────────→│
       │                               │                            │
       │                               │  Check: has_medical_report │
       │                               │  ✓ YES → Proceed          │
       │                               │  ✗ NO  → BLOCK            │
       │                               │                            │
       │                               │ Retrieve from BOTH:        │
       │                               │                      ┌─────┴──────┐
       │                               ├──────────────────→  │   Shared    │
       │                               │  Search "symptoms"  │   Medical   │
       │                               │                     │   Books     │
       │                               │  ← k=3 chunks       │             │
       │                               │                     └─────────────┘
       │                               │
       │                               │                      ┌─────┬──────┐
       │                               ├──────────────────→  │ Patient      │
       │                               │  Search "symptoms"  │ Reports      │
       │                               │                     │ (P001)       │
       │                               │  ← k=3 chunks       │              │
       │                               │                     └──────────────┘
       │                               │
       │                               │  Merge & Prepare Context:
       │                               │  ┌──────────────────────────┐
       │                               │  │ Shared (3 chunks):       │
       │                               │  │ • Guidelines             │
       │                               │  │ • Evidence               │
       │                               │  │                          │
       │                               │  │ Patient (3 chunks):      │
       │                               │  │ • Patient's history      │
       │                               │  │ • Medications            │
       │                               │  │ • Discharge data         │
       │                               │  │                          │
       │                               │  │ = 6 chunks total context │
       │                               │  └──────────────────────────┘
       │                               │
       │                               │  Call LLM with merged context:
       │                               ├──────────→ Groq API ──→ Personalized
       │                               │           mixtral     Answer
       │                               │           8x7b        + Risk
       │                               │                       Assessment
       │                               │
       │← Answer + Risk Level ─────────│
       │  + Clinical Reasoning         │
       │  + Recommendations            │


═══════════════════════════════════════════════════════════════════════════════
PHASE 5: MONITORING SESSION - PERSONALIZED QUESTIONS
═══════════════════════════════════════════════════════════════════════════════

    Frontend                       Backend API              RAG Context
       │                               │                        │
       │ 5. Start Monitoring          │                        │
       │─────────────────→ POST /session/start ────────────→│
       │                               │                        │
       │                               │  Check: has_medical_   │
       │                               │         report?        │
       │                               │  ✓ YES → Create session│
       │                               │  ✗ NO  → BLOCK         │
       │                               │                        │
       │← Session Created ─────────────│                        │
       │  session_id: "abc-123-..."    │                        │
       │  max_questions: 6             │                        │
       │                               │                        │
       │ Loop: Question 1-6            │                        │
       │ ┌─────────────────────────────┘                        │
       │ │                                                       │
       │ │ Get Next Question                                    │
       │ │─────────────────→ POST /next-question ────────────→│
       │ │                               │                      │
       │ │                               │ Generate using:      │
       │ │                               │ • Patient symptoms   │
       │ │                               │ • Patient context    │
       │ │                               │ • Medical guidelines│
       │ │                               │ • Previous answers  │
       │ │                               │ (from both stores) │
       │ │                               │                      │
       │ │← Question #1 ──────────────────│                    │
       │ │  "Any weakness in arms/legs?"  │                    │
       │ │                               │                      │
       │ │ Submit Answer                 │                      │
       │ │─────────────────→ POST /submit-answer             │
       │ │  { answer: "No" }             │                    │
       │ │                               │                      │
       │ │← Acknowledged ──────────────────│                    │
       │ │                               │                      │
       │ └─────────────────→ [REPEAT for questions 2-6]         │
       │                               │                        │
       │                               │                        │
       │ Get Final Assessment          │                        │
       │─────────────────→ POST /assessment ───────────────→│
       │                               │                        │
       │                               │ Risk Assessment Using: │
       │                               │ • All symptoms         │
       │                               │ • Both RAG stores      │
       │                               │ • Clinical guidelines  │
       │                               │ • Patient risk factors │
       │                               │                        │
       │← Risk Level: LOW ──────────────│                        │
       │  Reason: [...]                │                        │
       │  Action: [...]                │                        │


═══════════════════════════════════════════════════════════════════════════════
KEY DECISION GATES
═══════════════════════════════════════════════════════════════════════════════

    Gate 1: Initial Access
    ─────────────────────
    Has report uploaded?
         ├─ NO  ────→ Block all features
         │           Show upload form
         └─ YES ────→ Enable all features

    Gate 2: Chat Initiation
    ──────────────────────
    Before POST /chat/query:
         ├─ NO report ────→ HTTP 400 Error
         │                  "Report required"
         └─ HAS report ────→ Proceed to RAG
                            Retrieve + Generate

    Gate 3: Monitoring Session
    ──────────────────────────
    Before POST /session/start:
         ├─ NO report ────→ HTTP 400 Error
         │                  "Report required"
         └─ HAS report ────→ Create session
                            Generate questions


═══════════════════════════════════════════════════════════════════════════════
ERROR HANDLING
═══════════════════════════════════════════════════════════════════════════════

    Upload Fails:
    ─────────────
    PDF not readable
         ↓
    400 Bad Request
         ↓
    "Text extraction failed: [reason]"
         ↓
    Frontend shows error
    User retries with different file

    Chat Blocked:
    ────────────
    No vector store for patient
         ↓
    400 Bad Request
         ↓
    "Medical reports required..."
         ↓
    Frontend redirects to upload
    User uploads file first


═══════════════════════════════════════════════════════════════════════════════
DATA FLOW SUMMARY
═══════════════════════════════════════════════════════════════════════════════

    Medical Report File
           ↓
    [Report Processor] ← Extract, Clean, Chunk
           ↓
    Text Chunks
           ↓
    [Embedding Engine] ← Generate 384-dim vectors
           ↓
    Embedded Vectors
           ↓
    [FAISS Vector Store] ← Index & save
           ↓
    Patient Vector DB Created
           ↓
    [Status Flag Updated] ← has_medical_report = TRUE
           ↓
    [Chat Enabled]
           ↓
    User Question
           ↓
    [Dual RAG Retrieval]
    ├─ Search Shared Store (medical guidelines)
    └─ Search Patient Store (medical history)
           ↓
    [Merged Context]
           ↓
    [Groq LLM]
           ↓
    Personalized Answer
           ↓
    Frontend Display


═══════════════════════════════════════════════════════════════════════════════

CRITICAL RULES:
───────────────

1. ✓ MUST: Check /report/status FIRST
2. ✓ MUST: Upload report BEFORE chat
3. ✓ MUST: Use dual RAG sources (shared + patient)
4. ✓ MUST: Gate chat on report existence
5. ✗ MUST NOT: Diagnose patients
6. ✗ MUST NOT: Prescribe medications
7. ✗ MUST NOT: Share patient data across patients

═══════════════════════════════════════════════════════════════════════════════
