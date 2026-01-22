from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.patient import Patient
from ..schemas.user import PatientResponse
from ..utils.dependencies import get_current_nurse

router = APIRouter(prefix="/nurse", tags=["Nurse"])


@router.get("/patients", response_model=List[PatientResponse])
async def get_ward_patients(
    current_user: User = Depends(get_current_nurse),
    db: Session = Depends(get_db)
):
    """Get all patients in nurse's assigned ward."""
    
    nurse = current_user.nurse
    if not nurse:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nurse profile not found"
        )
    
    # Get patients in the same ward
    patients = (
        db.query(Patient)
        .options(joinedload(Patient.user))
        .filter(Patient.ward == nurse.ward_assigned)
        .all()
    )
    
    # Format response
    patient_list = []
    for patient in patients:
        patient_list.append({
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
        })
    
    return patient_list


@router.get("/alerts")
async def get_nurse_alerts(current_user: User = Depends(get_current_nurse)):
    """Get all active alerts for nurse's ward (redirects to /api/alerts endpoint)"""
    return {
        "message": "Please use GET /api/alerts endpoint to retrieve alerts",
        "note": "The alerts endpoint handles role-based filtering automatically"
    }
