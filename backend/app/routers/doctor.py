from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.patient import Patient
from ..schemas.user import PatientResponse
from ..utils.dependencies import get_current_doctor

router = APIRouter(prefix="/doctor", tags=["Doctor"])


@router.get("/patients", response_model=List[PatientResponse])
async def get_assigned_patients(
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """Get all patients assigned to the current doctor."""
    
    # Get doctor record
    doctor = current_user.doctor
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get assigned patients with user information
    patients = (
        db.query(Patient)
        .options(joinedload(Patient.user))
        .filter(Patient.assigned_doctor_id == doctor.id)
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


@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient_details(
    patient_id: int,
    current_user: User = Depends(get_current_doctor),
    db: Session = Depends(get_db)
):
    """Get specific patient details (must be assigned to current doctor)."""
    
    doctor = current_user.doctor
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )
    
    # Get patient with user information
    patient = (
        db.query(Patient)
        .options(joinedload(Patient.user))
        .filter(Patient.id == patient_id, Patient.assigned_doctor_id == doctor.id)
        .first()
    )
    
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found or not assigned to you"
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


@router.get("/alerts")
async def get_doctor_alerts(current_user: User = Depends(get_current_doctor)):
    """Get all alerts for doctor's patients (placeholder for future)."""
    return {
        "message": "Alert functionality will be implemented in STEP 2",
        "alerts": []
    }
