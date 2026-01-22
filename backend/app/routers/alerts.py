from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models.user import User
from ..models.alert import Alert, AlertStatus
from ..models.patient import Patient
from ..schemas.alert import AlertCreate, AlertResponse, AlertAcknowledge
from ..utils.dependencies import get_current_doctor, get_current_nurse, get_current_user
from ..config import settings

router = APIRouter(prefix="/alerts", tags=["Alerts"])


def verify_edge_device_api_key(x_api_key: str = Header(...)):
    """Verify edge device API key"""
    if x_api_key != settings.EDGE_DEVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_edge_device_api_key)
):
    """
    Create a new alert from edge device.
    Requires X-API-Key header for authentication.
    """
    # Verify patient exists
    patient = db.query(Patient).filter(Patient.id == alert.patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with id {alert.patient_id} not found"
        )
    
    # Create new alert
    new_alert = Alert(
        patient_id=alert.patient_id,
        alert_type=alert.alert_type,
        message=alert.message,
        severity=alert.severity,
        source=alert.source,
        status=AlertStatus.NEW
    )
    
    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)
    
    return {
        "status": "success",
        "message": "Alert created successfully",
        "alert_id": new_alert.id
    }


@router.get("", response_model=List[AlertResponse])
async def get_alerts(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get alerts based on user role.
    - Doctor: alerts for assigned patients
    - Nurse: all alerts in their ward
    - Admin: all alerts
    """
    query = db.query(Alert).options(
        joinedload(Alert.patient).joinedload(Patient.user),
        joinedload(Alert.acknowledged_by_user)
    )
    
    # Filter by status if provided
    if status_filter:
        if status_filter.upper() == "NEW":
            query = query.filter(Alert.status == AlertStatus.NEW)
        elif status_filter.upper() == "ACKNOWLEDGED":
            query = query.filter(Alert.status == AlertStatus.ACKNOWLEDGED)
    
    # Role-based filtering
    if current_user.role.value == "doctor":
        # Get doctor's assigned patients
        doctor = current_user.doctor
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor profile not found"
            )
        
        # Filter alerts for doctor's patients
        patient_ids = [p.id for p in doctor.patients]
        query = query.filter(Alert.patient_id.in_(patient_ids))
    
    elif current_user.role.value == "nurse":
        # Get nurse's ward patients
        nurse = current_user.nurse
        if not nurse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nurse profile not found"
            )
        
        # Filter alerts for patients in nurse's ward
        ward_patient_ids = db.query(Patient.id).filter(
            Patient.ward == nurse.ward_assigned
        ).all()
        patient_ids = [pid[0] for pid in ward_patient_ids]
        query = query.filter(Alert.patient_id.in_(patient_ids))
    
    elif current_user.role.value == "admin":
        # Admin can see all alerts
        pass
    
    else:
        # Patients and other roles cannot access alerts
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden for this role"
        )
    
    # Order by newest first
    alerts = query.order_by(Alert.created_at.desc()).all()
    
    # Format response
    alert_list = []
    for alert in alerts:
        alert_list.append({
            "id": alert.id,
            "patient_id": alert.patient_id,
            "patient_name": alert.patient.user.full_name,
            "patient_number": alert.patient.patient_number,
            "alert_type": alert.alert_type,
            "message": alert.message,
            "severity": alert.severity,
            "source": alert.source,
            "status": alert.status,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_by_name": alert.acknowledged_by_user.full_name if alert.acknowledged_by_user else None,
            "acknowledged_at": alert.acknowledged_at,
            "created_at": alert.created_at
        })
    
    return alert_list


@router.post("/{alert_id}/acknowledge", response_model=dict)
async def acknowledge_alert(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert. Only doctors and nurses can acknowledge alerts.
    """
    # Check user role
    if current_user.role.value not in ["doctor", "nurse", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors and nurses can acknowledge alerts"
        )
    
    # Get alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Check if already acknowledged
    if alert.status == AlertStatus.ACKNOWLEDGED:
        return {
            "status": "info",
            "message": "Alert already acknowledged",
            "acknowledged_by": alert.acknowledged_by_user.full_name if alert.acknowledged_by_user else None,
            "acknowledged_at": alert.acknowledged_at
        }
    
    # Verify access based on role
    if current_user.role.value == "doctor":
        doctor = current_user.doctor
        patient_ids = [p.id for p in doctor.patients]
        if alert.patient_id not in patient_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only acknowledge alerts for your assigned patients"
            )
    
    elif current_user.role.value == "nurse":
        nurse = current_user.nurse
        patient = db.query(Patient).filter(Patient.id == alert.patient_id).first()
        if patient.ward != nurse.ward_assigned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only acknowledge alerts for patients in your ward"
            )
    
    # Update alert
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = datetime.utcnow()
    
    db.commit()
    db.refresh(alert)
    
    return {
        "status": "success",
        "message": "Alert acknowledged successfully",
        "alert_id": alert.id,
        "acknowledged_by": current_user.full_name,
        "acknowledged_at": alert.acknowledged_at
    }
