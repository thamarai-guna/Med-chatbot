"""
FastAPI Backend for Medical Chatbot
Extracts Streamlit logic into REST APIs
Production-ready interface for React frontend

This is the headless backend service.
The Streamlit app is a prototype for reference.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import sys

# Add parent directory to path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import existing business logic (NOT UI code)
from rag_engine import RAGEngine
from patient_manager import get_patient_manager
from daily_questions import DailyQuestionGenerator
from clinical_monitoring_prompts import (
    CLINICAL_MONITORING_SYSTEM_PROMPT,
    create_question_generation_prompt,
    create_risk_assessment_prompt,
    QuestionTracker,
    MedicalReportValidator,
    validate_json_response,
    validate_risk_level,
    validate_answer_type
)
from report_upload_engine import get_upload_handler

# Initialize FastAPI app
app = FastAPI(
    title="Medical Chatbot API",
    description="Headless backend for hospital medical chatbot",
    version="1.0.0"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# SESSION STORAGE FOR CLINICAL MONITORING
# ============================================================================

# In-memory session store (use Redis/database in production)
MONITORING_SESSIONS: Dict[str, Dict[str, Any]] = {}

def generate_session_id() -> str:
    """Generate unique session ID"""
    import uuid
    return str(uuid.uuid4())


# ============================================================================
# DATA MODELS (Request/Response schemas)
# ============================================================================

class ChatQueryRequest(BaseModel):
    """Chat query request"""
    patient_id: str
    message: str
    vector_store_name: Optional[str] = "DefaultVectorDB"

class ChatQueryResponse(BaseModel):
    """Chat query response"""
    patient_id: str
    question: str
    answer: str
    risk_level: str
    risk_reason: str
    source_documents: List[str]
    timestamp: str

class PatientRegisterRequest(BaseModel):
    """Patient registration request"""
    patient_id: str
    name: str
    email: Optional[str] = None
    age: Optional[int] = None
    medical_history: Optional[str] = None

class PatientInfo(BaseModel):
    """Patient information response"""
    patient_id: str
    name: str
    email: Optional[str]
    age: Optional[int]
    medical_history: Optional[str]
    created_at: str
    last_accessed: str

class ChatHistoryResponse(BaseModel):
    """Chat history item response"""
    id: int
    question: str
    answer: str
    risk_level: str
    risk_reason: str
    source_documents: List[str]
    timestamp: str

class RiskSummary(BaseModel):
    """Risk assessment summary"""
    patient_id: str
    total_queries: int
    max_risk_level: str
    risk_distribution: Dict[str, int]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str


# ============================================================================
# CLINICAL MONITORING MODELS
# ============================================================================

class MonitoringSessionStartRequest(BaseModel):
    """Start clinical monitoring session"""
    patient_id: str
    max_questions: Optional[int] = 6


class MonitoringQuestionResponse(BaseModel):
    """Clinical monitoring question response"""
    patient_id: str
    session_id: str
    question: str
    answer_type: str  # YES_NO, SCALE_0_10, SHORT_TEXT
    question_number: int
    total_expected: int


class MonitoringAnswerRequest(BaseModel):
    """Submit answer to monitoring question"""
    patient_id: str
    session_id: str
    question: str
    answer: str
    answer_type: str


class MonitoringAssessmentResponse(BaseModel):
    """Final clinical monitoring assessment"""
    patient_id: str
    session_id: str
    risk_level: str  # LOW, MEDIUM, HIGH
    reason: List[str]
    action: str
    total_questions_asked: int
    timestamp: str
    version: str

class DailyQuestionRequest(BaseModel):
    """Request for saving daily question answer"""
    question: str
    answer: str
    question_metadata: Optional[Dict[str, Any]] = None

# ============================================================================
# MEDICAL REPORT UPLOAD MODELS
# ============================================================================

class ReportUploadResponse(BaseModel):
    """Response for medical report upload"""
    success: bool
    patient_id: str
    filename: str
    message: str
    chunks_count: int
    timestamp: str

class ReportStatusResponse(BaseModel):
    """Check if patient has uploaded medical reports"""
    patient_id: str
    has_medical_report: bool
    status: str
    can_proceed_with_monitoring: bool

# ============================================================================
# LOGIN MODELS
# ============================================================================

class LoginRequest(BaseModel):
    """Login request"""
    username: str
    password: str

class LoginResponse(BaseModel):
    """Login response"""
    success: bool
    user_id: str
    role: str
    message: str

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

# Demo users database (in production, use proper authentication)
DEMO_USERS = {
    "patient1": {"password": "pass123", "role": "patient", "user_id": "P001"},
    "patient2": {"password": "pass123", "role": "patient", "user_id": "P002"},
    "doctor1": {"password": "pass123", "role": "doctor", "user_id": "D001"},
    "doctor2": {"password": "pass123", "role": "doctor", "user_id": "D002"},
    "nurse1": {"password": "pass123", "role": "nurse", "user_id": "N001"},
    "nurse2": {"password": "pass123", "role": "nurse", "user_id": "N002"},
}

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return role for dashboard routing"""
    username = request.username.strip()
    password = request.password.strip()
    
    # Check credentials
    if username not in DEMO_USERS or DEMO_USERS[username]["password"] != password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    user_info = DEMO_USERS[username]
    
    # For patient role, ensure patient exists in database
    if user_info["role"] == "patient":
        pm = get_patient_manager()
        patient = pm.get_patient(user_info["user_id"])
        if not patient:
            # Create patient if doesn't exist
            try:
                pm.register_patient(
                    patient_id=user_info["user_id"],
                    name=f"Patient {username}",
                    email=f"{username}@hospital.local",
                    age=None,
                    medical_history="Default medical history"
                )
            except:
                pass
    
    return LoginResponse(
        success=True,
        user_id=user_info["user_id"],
        role=user_info["role"],
        message=f"Login successful. Welcome {username}!"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )

# ============================================================================
# PATIENT ENDPOINTS
# ============================================================================

@app.post("/api/patient/register")
async def register_patient(request: PatientRegisterRequest):
    """Register a new patient"""
    try:
        pm = get_patient_manager()
        result = pm.register_patient(
            patient_id=request.patient_id,
            name=request.name,
            email=request.email,
            age=request.age,
            medical_history=request.medical_history
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "patient_id": request.patient_id
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patient/{patient_id}")
async def get_patient(patient_id: str):
    """Get patient information"""
    try:
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        return PatientInfo(**patient)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/patient")
async def list_all_patients():
    """List all registered patients"""
    try:
        pm = get_patient_manager()
        patients = pm.get_all_patients()
        return {
            "total": len(patients),
            "patients": patients
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHAT / RAG ENDPOINTS
# ============================================================================

@app.post("/api/chat/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest):
    """
    Main chat endpoint - ask medical question
    
    MANDATORY PRECONDITION: Medical report must be uploaded and indexed
    Uses dual RAG: shared medical books + patient-specific vector store
    
    BLOCKING RULE: If no medical report has been uploaded:
    - Chatbot is disabled
    - Returns blocking message
    - Patient must upload report first via /api/patient/{patient_id}/upload-report
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(request.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {request.patient_id} not found")
        
        # CRITICAL GATING: Check if patient has uploaded medical reports
        handler = get_upload_handler()
        upload_status = handler.get_upload_status(request.patient_id)
        
        if not upload_status["can_proceed_with_monitoring"]:
            # Block chat - medical report upload is required
            raise HTTPException(
                status_code=400,
                detail="Medical reports are required before chatbot interaction can begin. Please upload your medical reports first."
            )
        
        # Medical report exists - proceed with RAG query
        # Initialize RAG engine with dual vector store retrieval
        rag_engine = RAGEngine(
            patient_id=request.patient_id,
            max_tokens=500,
            temperature=0.7
        )
        
        # Get response (retrieves from both shared and patient stores)
        response = rag_engine.answer_question(request.message)
        
        return ChatQueryResponse(
            patient_id=request.patient_id,
            question=request.message,
            answer=response["answer"],
            risk_level=response["risk_level"],
            risk_reason=response["risk_reason"],
            source_documents=response["source_documents"],
            timestamp=datetime.now().isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/chat/history/{patient_id}")
async def get_chat_history(patient_id: str, limit: int = 50):
    """Get chat history for patient"""
    try:
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        history = pm.get_patient_history(patient_id, limit=limit)
        
        return {
            "patient_id": patient_id,
            "total": len(history),
            "history": [
                ChatHistoryResponse(
                    id=i,
                    question=h["question"],
                    answer=h["answer"],
                    risk_level=h["risk_level"],
                    risk_reason=h["risk_reason"],
                    source_documents=h["source_documents"],
                    timestamp=h["timestamp"]
                )
                for i, h in enumerate(history)
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/chat/history/{patient_id}")
async def clear_chat_history(patient_id: str):
    """Clear chat history for patient (GDPR right to be forgotten)"""
    try:
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        success = pm.clear_patient_history(patient_id)
        if success:
            return {"success": True, "message": f"Chat history cleared for patient {patient_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear history")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RISK ASSESSMENT ENDPOINTS
# ============================================================================

@app.get("/api/patient/{patient_id}/risk/summary", response_model=RiskSummary)
async def get_risk_summary(patient_id: str, days: int = 30):
    """Get risk assessment summary for patient"""
    try:
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        summary = pm.get_patient_risk_summary(patient_id, days=days)
        
        return RiskSummary(**summary)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DAILY QUESTION ENDPOINTS
# ============================================================================

@app.post("/api/questions/daily/{patient_id}")
async def generate_daily_question(patient_id: str):
    """
    Generate personalized daily symptom monitoring question
    
    Based on:
    - Patient's medical records
    - Shared medical knowledge
    - Recent chat history
    - Risk trends
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        # Generate question
        generator = DailyQuestionGenerator(patient_id)
        question = generator.generate_daily_question()
        
        return {
            "success": True,
            "patient_id": patient_id,
            **question
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/questions/daily/{patient_id}/answer")
async def save_daily_answer(patient_id: str, request: DailyQuestionRequest):
    """
    Save patient's answer to daily question
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        # Save answer
        generator = DailyQuestionGenerator(patient_id)
        success = generator.save_daily_answer(
            question=request.question,
            answer=request.answer,
            question_metadata=request.question_metadata
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save answer")
        
        return {
            "success": True,
            "message": "Daily answer saved successfully",
            "patient_id": patient_id,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questions/daily/{patient_id}/history")
async def get_daily_answers_history(patient_id: str, days: int = 7):
    """
    Get patient's recent daily question answers
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        # Get history
        generator = DailyQuestionGenerator(patient_id)
        history = generator.get_recent_daily_answers(days=days)
        
        return {
            "patient_id": patient_id,
            "days": days,
            "total": len(history),
            "history": history
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DOCUMENT MANAGEMENT ENDPOINTS (PATIENT-SPECIFIC)
# ============================================================================

@app.post("/api/documents/patient/{patient_id}/upload")
async def upload_patient_documents(
    patient_id: str,
    files: List[UploadFile] = File(...),
    uploader_role: str = "patient",  # "patient" or "nurse"
    chunk_size: int = 512,
    chunk_overlap: int = 50
):
    """
    Upload patient-specific medical records
    
    Documents are:
    - Saved to: patient_records/{patient_id}/
    - Embedded to: vector_store/patient_{patient_id}/
    - Private to this patient only
    """
    try:
        import falcon
        
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Create patient directories
        patient_records_dir = f"patient_records/{patient_id}"
        os.makedirs(patient_records_dir, exist_ok=True)
        
        # Process and save files
        combined_content = ""
        saved_files = []
        
        for file in files:
            # Save original file
            file_path = os.path.join(patient_records_dir, file.filename)
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
                saved_files.append(file.filename)
            
            # Extract text content
            await file.seek(0)  # Reset file pointer
            if file.filename.endswith(".pdf"):
                combined_content += falcon.read_pdf(file.file)
            elif file.filename.endswith(".txt"):
                combined_content += falcon.read_txt(file.file)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}"
                )
        
        if not combined_content:
            raise HTTPException(status_code=400, detail="No content extracted from files")
        
        # Chunk documents
        split_docs = falcon.split_doc(combined_content, chunk_size, chunk_overlap)
        
        # Embed into patient-specific vector store
        patient_vector_store = f"patient_{patient_id}"
        
        # Check if patient vector store already exists
        patient_vs_path = f"vector store/{patient_vector_store}"
        merge_with_existing = os.path.exists(patient_vs_path)
        
        falcon.embedding_storing(
            split=split_docs,
            create_new_vs=not merge_with_existing,
            existing_vector_store="" if not merge_with_existing else patient_vector_store,
            new_vs_name=patient_vector_store
        )
        
        return {
            "success": True,
            "message": f"Uploaded {len(files)} medical record(s) for patient {patient_id}",
            "patient_id": patient_id,
            "files_saved": saved_files,
            "chunks_created": len(split_docs),
            "vector_store": patient_vector_store,
            "uploader_role": uploader_role,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/patient/{patient_id}/list")
async def list_patient_documents(patient_id: str):
    """
    List all medical records uploaded for a patient
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        patient_records_dir = f"patient_records/{patient_id}"
        
        if not os.path.exists(patient_records_dir):
            return {
                "patient_id": patient_id,
                "documents": [],
                "total": 0
            }
        
        files = []
        for filename in os.listdir(patient_records_dir):
            file_path = os.path.join(patient_records_dir, filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size_bytes": stat.st_size,
                    "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return {
            "patient_id": patient_id,
            "documents": files,
            "total": len(files)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/documents/patient/{patient_id}/{filename}")
async def delete_patient_document(patient_id: str, filename: str):
    """
    Delete a specific medical record for a patient
    
    NOTE: This only deletes the file, not the embeddings.
    Vector store rebuild needed for complete removal.
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        file_path = f"patient_records/{patient_id}/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Document {filename} not found")
        
        os.remove(file_path)
        
        return {
            "success": True,
            "message": f"Deleted document {filename} for patient {patient_id}",
            "patient_id": patient_id,
            "filename": filename,
            "note": "Vector store embeddings still exist. Re-upload remaining documents to rebuild.",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MEDICAL REPORT VALIDATION ENDPOINT
# ============================================================================


# REMOVED: This endpoint was duplicated - keeping the newer version below with proper implementation

# ============================================================================
# CLINICAL MONITORING ENDPOINTS
# ============================================================================


@app.post("/api/monitoring/session/start")
async def start_monitoring_session(request: MonitoringSessionStartRequest):
    """Start a new clinical monitoring session for a patient
    
    MANDATORY PRECONDITION: Medical report must be uploaded and indexed
    
    BLOCKING RULE: If no medical report has been uploaded:
    - Monitoring is disabled
    - Returns blocking message
    - Patient must upload report first via /api/patient/{patient_id}/upload-report
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(request.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {request.patient_id} not found")
        
        # CRITICAL GATING: Check if patient has uploaded medical reports
        handler = get_upload_handler()
        upload_status = handler.get_upload_status(request.patient_id)
        
        if not upload_status["can_proceed_with_monitoring"]:
            # Block monitoring session - medical report upload is required
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "NO_MEDICAL_REPORT",
                    "message": "Medical reports are required before symptom monitoring can begin.",
                    "action": "Please upload your medical reports using the Report Upload section."
                }
            )
        
        # Medical report exists - proceed with session creation
        session_id = generate_session_id()
        MONITORING_SESSIONS[session_id] = {
            "patient_id": request.patient_id,
            "max_questions": request.max_questions or 6,
            "question_tracker": QuestionTracker(),
            "responses": {},  # {question: answer}
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        return {
            "success": True,
            "session_id": session_id,
            "patient_id": request.patient_id,
            "max_questions": request.max_questions or 6,
            "message": "Monitoring session started. Ready for first question."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/monitoring/session/{session_id}/next-question")
async def get_next_monitoring_question(session_id: str):
    """Get next monitoring question for active session"""
    try:
        # Validate session exists
        if session_id not in MONITORING_SESSIONS:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        session = MONITORING_SESSIONS[session_id]
        if session["status"] != "active":
            raise HTTPException(status_code=400, detail="Session is not active")
        
        # Check if max questions reached
        tracker = session["question_tracker"]
        if not tracker.can_ask_more(session["max_questions"]):
            return {
                "session_id": session_id,
                "status": "complete",
                "message": "Maximum questions reached. Ready for assessment.",
                "question": None
            }
        
        # Get patient info
        pm = get_patient_manager()
        patient = pm.get_patient(session["patient_id"])
        patient_history = patient.get("medical_history", "No previous history")
        
        # Get RAG guidance
        try:
            rag_engine = RAGEngine(patient_id=session["patient_id"])
            guidance = rag_engine.retrieve_documents("neurological symptoms monitoring")
            retrieved_guidance = " ".join([doc.page_content for doc in guidance[:3]]) if guidance else ""
        except:
            retrieved_guidance = ""
        
        # Generate question using LLM
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        question_prompt = create_question_generation_prompt(
            patient_history=patient_history,
            previous_answers=session["responses"],
            current_question_number=tracker.question_count + 1,
            max_questions=session["max_questions"],
            retrieved_medical_guidance=retrieved_guidance
        )
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": CLINICAL_MONITORING_SYSTEM_PROMPT},
                {"role": "user", "content": question_prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content
        
        # Parse JSON response
        import json
        try:
            question_data = json.loads(response_text)
            if not validate_json_response(response_text) or not validate_answer_type(question_data.get("answer_type", "")):
                raise ValueError("Invalid question format")
        except:
            raise HTTPException(status_code=500, detail="Failed to generate valid question")
        
        # Record question
        tracker.add_question(question_data["question"])
        
        return MonitoringQuestionResponse(
            patient_id=session["patient_id"],
            session_id=session_id,
            question=question_data["question"],
            answer_type=question_data["answer_type"],
            question_number=question_data["question_number"],
            total_expected=question_data["total_expected"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/monitoring/session/{session_id}/submit-answer")
async def submit_monitoring_answer(session_id: str, request: MonitoringAnswerRequest):
    """Submit answer to monitoring question"""
    try:
        # Validate session
        if session_id not in MONITORING_SESSIONS:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        session = MONITORING_SESSIONS[session_id]
        if session["status"] != "active":
            raise HTTPException(status_code=400, detail="Session is not active")
        
        # Validate answer type
        if not validate_answer_type(request.answer_type):
            raise HTTPException(status_code=400, detail="Invalid answer type")
        
        # Validate answer content
        if request.answer_type == "YES_NO" and request.answer.upper() not in ["YES", "NO"]:
            raise HTTPException(status_code=400, detail="YES_NO answer must be YES or NO")
        
        if request.answer_type == "SCALE_0_10":
            try:
                scale_val = int(request.answer)
                if not (0 <= scale_val <= 10):
                    raise ValueError
            except:
                raise HTTPException(status_code=400, detail="SCALE answer must be 0-10")
        
        # Store response
        session["responses"][request.question] = request.answer
        
        # Track negative responses to avoid repetition
        if request.answer_type == "YES_NO" and request.answer.upper() == "NO":
            session["question_tracker"].mark_negative_response(request.question)
        
        return {
            "success": True,
            "session_id": session_id,
            "question_recorded": request.question,
            "message": "Answer recorded. Ready for next question."
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/monitoring/session/{session_id}/assessment")
async def get_monitoring_assessment(session_id: str):
    """Get final clinical assessment for monitoring session"""
    try:
        # Validate session
        if session_id not in MONITORING_SESSIONS:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        session = MONITORING_SESSIONS[session_id]
        
        # Get patient info
        pm = get_patient_manager()
        patient = pm.get_patient(session["patient_id"])
        patient_history = patient.get("medical_history", "No previous history")
        
        # Get RAG guidance
        try:
            rag_engine = RAGEngine(patient_id=session["patient_id"])
            guidance = rag_engine.retrieve_documents("neurological symptoms risk assessment")
            retrieved_guidance = " ".join([doc.page_content for doc in guidance[:3]]) if guidance else ""
        except:
            retrieved_guidance = ""
        
        # Generate risk assessment using LLM
        from groq import Groq
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        assessment_prompt = create_risk_assessment_prompt(
            patient_history=patient_history,
            monitoring_responses=session["responses"],
            retrieved_medical_guidance=retrieved_guidance
        )
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": CLINICAL_MONITORING_SYSTEM_PROMPT},
                {"role": "user", "content": assessment_prompt}
            ],
            temperature=0.5,
            max_tokens=400
        )
        
        response_text = response.choices[0].message.content
        
        # Parse assessment JSON
        import json
        try:
            assessment_data = json.loads(response_text)
            if not validate_risk_level(assessment_data.get("risk_level", "")):
                raise ValueError("Invalid risk level")
        except:
            raise HTTPException(status_code=500, detail="Failed to generate valid assessment")
        
        # Mark session complete
        session["status"] = "complete"
        session["assessment"] = assessment_data
        session["completed_at"] = datetime.now().isoformat()
        
        # Store in patient history
        pm.add_to_patient_history(
            patient_id=session["patient_id"],
            question="Clinical Monitoring Session",
            answer=json.dumps(session["responses"]),
            risk_level=assessment_data["risk_level"],
            risk_reason=" / ".join(assessment_data["reason"]),
            source_documents=[]
        )
        
        return MonitoringAssessmentResponse(
            patient_id=session["patient_id"],
            session_id=session_id,
            risk_level=assessment_data["risk_level"],
            reason=assessment_data["reason"],
            action=assessment_data["action"],
            total_questions_asked=session["question_tracker"].question_count,
            timestamp=session["completed_at"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/monitoring/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current status of monitoring session"""
    try:
        if session_id not in MONITORING_SESSIONS:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        session = MONITORING_SESSIONS[session_id]
        
        return {
            "session_id": session_id,
            "patient_id": session["patient_id"],
            "status": session["status"],
            "questions_asked": session["question_tracker"].question_count,
            "max_questions": session["max_questions"],
            "created_at": session["created_at"],
            "completed_at": session.get("completed_at"),
            "assessment": session.get("assessment") if session["status"] == "complete" else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# MEDICAL REPORT UPLOAD ENDPOINTS
# ============================================================================
# Gateway for RAG system initialization
# Reports MUST be uploaded before chatbot/monitoring becomes active

@app.post("/api/patient/{patient_id}/upload-report", response_model=ReportUploadResponse)
async def upload_medical_report(
    patient_id: str,
    file: UploadFile = File(...)
):
    """
    Upload patient medical report (PDF, image, or text)
    
    CRITICAL SYSTEM FUNCTION:
    1. Validates patient exists
    2. Extracts text from file
    3. Chunks and embeds text
    4. Stores in patient-specific vector store
    5. Enables RAG-guided chatbot and monitoring
    
    Supported formats:
    - PDF (.pdf)
    - Images with OCR (.jpg, .jpeg, .png)
    - Plain text (.txt)
    
    Returns:
        ReportUploadResponse with success/chunks_count/message
    """
    try:
        print(f"[UPLOAD DEBUG] Patient ID: {patient_id}")
        print(f"[UPLOAD DEBUG] File received: {file.filename if file else 'None'}")
        print(f"[UPLOAD DEBUG] File size: {file.size if file else 'None'}")
        print(f"[UPLOAD DEBUG] File content type: {file.content_type if file else 'None'}")
        
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            print(f"[UPLOAD ERROR] Patient not found: {patient_id}")
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        if not file:
            print("[UPLOAD ERROR] No file provided")
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Get upload handler
        handler = get_upload_handler()
        
        # Save uploaded file
        file_bytes = await file.read()
        print(f"[UPLOAD DEBUG] File bytes read: {len(file_bytes)}")
        
        success, file_path = handler.save_uploaded_file(file_bytes, file.filename)
        
        if not success:
            print(f"[UPLOAD ERROR] Failed to save file: {file_path}")
            raise HTTPException(status_code=400, detail=file_path)
        
        print(f"[UPLOAD DEBUG] File saved to: {file_path}")
        
        # Process report: extract -> chunk -> embed -> store in vector DB
        result = handler.process_and_index_report(patient_id, file_path, file.filename)
        
        if not result["success"]:
            error_msg = result.get("message", "Unknown error during processing")
            print(f"[UPLOAD ERROR] Processing failed: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        print(f"[UPLOAD SUCCESS] Report processed: {result['chunks_count']} chunks")
        
        return ReportUploadResponse(
            success=True,
            patient_id=patient_id,
            filename=file.filename,
            message=result["message"],
            chunks_count=result["chunks_count"],
            timestamp=result["timestamp"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report upload failed: {str(e)}")


@app.get("/api/patient/{patient_id}/report/status", response_model=ReportStatusResponse)
async def check_medical_report_status(patient_id: str):
    """
    CHECK IF PATIENT HAS UPLOADED MEDICAL REPORTS
    
    THIS ENDPOINT MUST BE CALLED FIRST before any monitoring/chat
    
    Returns:
        has_medical_report: Boolean flag enabling/disabling chatbot
        can_proceed_with_monitoring: Must be true to proceed
        
    If False:
        - Chatbot is BLOCKED
        - Monitoring is BLOCKED
        - Return gating message to frontend
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        # Check if patient has vector store (reports uploaded)
        handler = get_upload_handler()
        status = handler.get_upload_status(patient_id)
        
        return ReportStatusResponse(
            patient_id=patient_id,
            has_medical_report=status["has_medical_report"],
            status=status["status"],
            can_proceed_with_monitoring=status["can_proceed_with_monitoring"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "Medical Chatbot Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "critical_requirement": "Medical reports must be uploaded before monitoring can begin",
        "endpoints": {
            "health": "GET /health",
            "patients": {
                "register": "POST /api/patient/register",
                "get": "GET /api/patient/{patient_id}",
                "list": "GET /api/patient",
                "check_report_status": "GET /api/patient/{patient_id}/report/status",
                "risk_summary": "GET /api/patient/{patient_id}/risk/summary"
            },
            "chat": {
                "query": "POST /api/chat/query (requires medical report)",
                "history": "GET /api/chat/history/{patient_id}",
                "clear_history": "DELETE /api/chat/history/{patient_id}"
            },
            "clinical_monitoring": {
                "description": "All monitoring endpoints require valid medical report",
                "start_session": "POST /api/monitoring/session/start (requires medical report)",
                "next_question": "POST /api/monitoring/session/{session_id}/next-question",
                "submit_answer": "POST /api/monitoring/session/{session_id}/submit-answer",
                "get_assessment": "POST /api/monitoring/session/{session_id}/assessment",
                "session_status": "GET /api/monitoring/session/{session_id}"
            },
            "documents": {
                "upload": "POST /api/documents/upload"
            }
        }
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )

# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize resources on startup"""
    print("[OK] Medical Chatbot API starting...")
    try:
        pm = get_patient_manager()
        print("[OK] Patient manager initialized")
        print("[OK] Database connection verified")
    except Exception as e:
        print(f"[ERROR] Startup failed: {e}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise so uvicorn knows about the error

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("[SHUTDOWN] Medical Chatbot API shutting down...")

# NOTE: Only run directly if needed for development
# When using: python -m uvicorn backend_api:app, the if __name__ block is not executed
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(
#         app,
#         host="0.0.0.0",
#         port=8000,
#         log_level="info"
#     )
