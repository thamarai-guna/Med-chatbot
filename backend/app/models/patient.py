from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Date, Text
from sqlalchemy.orm import relationship
from ..database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    patient_number = Column(String(50), unique=True)
    date_of_birth = Column(Date)
    gender = Column(String(20))
    admission_date = Column(DateTime(timezone=True))
    discharge_date = Column(DateTime(timezone=True), nullable=True)
    assigned_doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True, index=True)
    medical_history = Column(Text)
    is_discharged = Column(Boolean, default=False)
    ward = Column(String(100))
    bed_number = Column(String(20))

    # Relationships
    user = relationship("User", back_populates="patient")
    assigned_doctor = relationship("Doctor", back_populates="patients")

    def __repr__(self):
        return f"<Patient(id={self.id}, patient_number={self.patient_number})>"
