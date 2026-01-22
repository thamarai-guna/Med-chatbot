from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from ..database import get_db
from ..models.user import User
from ..models.patient import Patient
from ..schemas.user import PatientResponse
from ..utils.dependencies import get_current_patient

router = APIRouter(prefix="/patient", tags=["Patient"])


@router.get("/profile", response_model=PatientResponse)
async def get_patient_profile(
    current_user: User = Depends(get_current_patient),
    db: Session = Depends(get_db)
):
    """Get current patient's profile information."""
    
    patient = (
        db.query(Patient)
        .options(joinedload(Patient.user))
        .filter(Patient.user_id == current_user.id)
        .first()
    )
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    
    return {
        "id": patient.id,
        "user_id": patient.user_id,
        "patient_number": patient.patient_number,
        "full_name": patient.user.full_name,
        "email": patient.user.email,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "admission_date": patient.admission_date,
        "discharge_date": patient.discharge_date,
        "assigned_doctor_id": patient.assigned_doctor_id,
        "is_discharged": patient.is_discharged,
        "ward": patient.ward,
        "bed_number": patient.bed_number
    }


@router.get("/chat")
async def get_chat_history(current_user: User = Depends(get_current_patient)):
    """Get patient's chat history with AI assistant (placeholder for future)."""
    return {
        "message": "Chat functionality will be implemented in STEP 4",
        "chat_history": []
    }


@router.post("/chat")
async def send_chat_message(current_user: User = Depends(get_current_patient)):
    """Send message to AI chatbot (placeholder for future)."""
    return {
        "message": "Chat functionality will be implemented in STEP 4"
    }
