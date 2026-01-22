from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models.user import User, UserRole
from ..models.doctor import Doctor
from ..models.nurse import Nurse
from ..models.patient import Patient
from ..schemas.auth import RegisterRequest, UserResponse
from ..schemas.user import PatientCreate, DoctorCreate, NurseCreate, PatientResponse
from ..utils.dependencies import get_current_admin
from ..utils.security import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: RegisterRequest,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a new user with any role (admin only)."""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        role=request.role,
        full_name=request.full_name,
        phone=request.phone,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all users in the system (admin only)."""
    users = db.query(User).all()
    return users


@router.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def register_patient(
    request: PatientCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Register a new patient with full profile (admin only)."""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if patient number already exists
    existing_patient = db.query(Patient).filter(
        Patient.patient_number == request.patient_number
    ).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient number already exists"
        )
    
    # Verify doctor exists if assigned
    if request.assigned_doctor_id:
        doctor = db.query(Doctor).filter(Doctor.id == request.assigned_doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned doctor not found"
            )
    
    # Create user account
    new_user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        role=UserRole.PATIENT,
        full_name=request.full_name,
        phone=request.phone,
        is_active=True
    )
    
    db.add(new_user)
    db.flush()  # Get user.id without committing
    
    # Create patient profile
    new_patient = Patient(
        user_id=new_user.id,
        patient_number=request.patient_number,
        date_of_birth=request.date_of_birth,
        gender=request.gender,
        admission_date=datetime.utcnow(),
        assigned_doctor_id=request.assigned_doctor_id,
        medical_history=request.medical_history,
        ward=request.ward,
        bed_number=request.bed_number,
        is_discharged=False
    )
    
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    return {
        "id": new_patient.id,
        "user_id": new_user.id,
        "patient_number": new_patient.patient_number,
        "full_name": new_user.full_name,
        "email": new_user.email,
        "date_of_birth": new_patient.date_of_birth,
        "gender": new_patient.gender,
        "admission_date": new_patient.admission_date,
        "discharge_date": new_patient.discharge_date,
        "assigned_doctor_id": new_patient.assigned_doctor_id,
        "is_discharged": new_patient.is_discharged,
        "ward": new_patient.ward,
        "bed_number": new_patient.bed_number
    }


@router.post("/doctors/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_doctor_profile(
    user_id: int,
    request: DoctorCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create doctor profile for existing user (admin only)."""
    
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.DOCTOR).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or not a doctor"
        )
    
    # Check if doctor profile already exists
    if user.doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor profile already exists"
        )
    
    new_doctor = Doctor(
        user_id=user_id,
        specialization=request.specialization,
        license_number=request.license_number,
        department=request.department
    )
    
    db.add(new_doctor)
    db.commit()
    db.refresh(new_doctor)
    
    return {"message": "Doctor profile created successfully", "doctor_id": new_doctor.id}


@router.post("/nurses/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_nurse_profile(
    user_id: int,
    request: NurseCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create nurse profile for existing user (admin only)."""
    
    user = db.query(User).filter(User.id == user_id, User.role == UserRole.NURSE).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or not a nurse"
        )
    
    # Check if nurse profile already exists
    if user.nurse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nurse profile already exists"
        )
    
    new_nurse = Nurse(
        user_id=user_id,
        ward_assigned=request.ward_assigned,
        shift=request.shift
    )
    
    db.add(new_nurse)
    db.commit()
    db.refresh(new_nurse)
    
    return {"message": "Nurse profile created successfully", "nurse_id": new_nurse.id}
