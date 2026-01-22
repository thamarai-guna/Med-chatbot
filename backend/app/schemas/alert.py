from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.alert import AlertType, AlertSeverity, AlertSource, AlertStatus


class AlertCreate(BaseModel):
    """Schema for creating an alert from edge device"""
    patient_id: int
    alert_type: AlertType
    message: str
    severity: AlertSeverity
    source: AlertSource


class AlertResponse(BaseModel):
    """Schema for alert response"""
    id: int
    patient_id: int
    patient_name: str
    patient_number: str
    alert_type: AlertType
    message: str
    severity: AlertSeverity
    source: AlertSource
    status: AlertStatus
    acknowledged_by: Optional[int] = None
    acknowledged_by_name: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertAcknowledge(BaseModel):
    """Schema for acknowledging an alert"""
    pass  # Empty body, user comes from token
