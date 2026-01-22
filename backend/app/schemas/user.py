from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date


class DoctorCreate(BaseModel):
    specialization: Optional[str] = None
    license_number: Optional[str] = None
    department: Optional[str] = None


class NurseCreate(BaseModel):
    ward_assigned: Optional[str] = None
    shift: Optional[str] = None


class PatientCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    patient_number: str
    date_of_birth: date
    gender: str
    assigned_doctor_id: Optional[int] = None
    medical_history: Optional[str] = None
    ward: Optional[str] = None
    bed_number: Optional[str] = None


class PatientResponse(BaseModel):
    id: int
    user_id: int
    patient_number: str
    full_name: str
    email: str
    date_of_birth: date
    gender: str
    admission_date: Optional[datetime]
    discharge_date: Optional[datetime]
    assigned_doctor_id: Optional[int]
    is_discharged: bool
    ward: Optional[str]
    bed_number: Optional[str]

    class Config:
        from_attributes = True


class DoctorResponse(BaseModel):
    id: int
    user_id: int
    full_name: str
    email: str
    specialization: Optional[str]
    license_number: Optional[str]
    department: Optional[str]

    class Config:
        from_attributes = True
