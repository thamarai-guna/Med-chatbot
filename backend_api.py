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
    timestamp: str
    version: str

class DailyQuestionRequest(BaseModel):
    """Request for saving daily question answer"""
    question: str
    answer: str
    question_metadata: Optional[Dict[str, Any]] = None

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

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
    
    Uses dual RAG: shared medical books + patient-specific records
    """
    try:
        # Validate patient exists
        pm = get_patient_manager()
        patient = pm.get_patient(request.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {request.patient_id} not found")
        
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
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint with API documentation"""
    return {
        "service": "Medical Chatbot Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "endpoints": {
            "health": "GET /health",
            "patients": {
                "register": "POST /api/patient/register",
                "get": "GET /api/patient/{patient_id}",
                "list": "GET /api/patient",
                "risk_summary": "GET /api/patient/{patient_id}/risk/summary"
            },
            "chat": {
                "query": "POST /api/chat/query",
                "history": "GET /api/chat/history/{patient_id}",
                "clear_history": "DELETE /api/chat/history/{patient_id}"
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
    print("✅ Medical Chatbot API starting...")
    try:
        pm = get_patient_manager()
        print("✅ Patient manager initialized")
        print("✅ Database connection verified")
    except Exception as e:
        print(f"⚠️ Startup warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Medical Chatbot API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
