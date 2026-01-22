from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    specialization = Column(String(100))
    license_number = Column(String(50))
    department = Column(String(100))

    # Relationships
    user = relationship("User", back_populates="doctor")
    patients = relationship("Patient", back_populates="assigned_doctor")

    def __repr__(self):
        return f"<Doctor(id={self.id}, specialization={self.specialization})>"
