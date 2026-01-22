from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base


class AlertType(str, enum.Enum):
    VITALS_ABNORMAL = "VITALS_ABNORMAL"
    COMA_MOVEMENT_DETECTED = "COMA_MOVEMENT_DETECTED"
    HIGH_RISK_FROM_CHATBOT = "HIGH_RISK_FROM_CHATBOT"


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AlertSource(str, enum.Enum):
    VITALS_EDGE = "vitals_edge"
    COMA_EDGE = "coma_edge"
    AI_CHATBOT = "ai_chatbot"


class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    alert_type = Column(Enum(AlertType), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    source = Column(Enum(AlertSource), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW, nullable=False, index=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    patient = relationship("Patient", backref="alerts")
    acknowledged_by_user = relationship("User", foreign_keys=[acknowledged_by])

    def __repr__(self):
        return f"<Alert(id={self.id}, patient_id={self.patient_id}, type={self.alert_type}, severity={self.severity})>"
