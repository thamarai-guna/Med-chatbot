"""Patient-related routes."""
from flask import Blueprint, jsonify, request
from models import User

# Create blueprint for patient routes
patient_bp = Blueprint('patient', __name__, url_prefix='/api')

@patient_bp.route('/patients', methods=['GET'])
def get_patients():
    """
    Get list of all patients (doctor only).
    
    For hackathon: No authentication check (frontend handles this).
    In production: Would verify doctor role via session/JWT.
    """
    patients = User.get_all_patients()
    
    return jsonify({
        'patients': patients
    }), 200


@patient_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """
    Get patient details by ID.
    
    Args:
        patient_id: Patient ID from URL
    """
    patient = User.get_patient_by_id(patient_id)
    
    if patient is None:
        return jsonify({'error': 'Patient not found'}), 404
    
    # In production: Add check-ins, vitals, etc.
    # For now: Just return patient info
    return jsonify({
        'patient': patient,
        'checkins': []  # Empty for skeleton
    }), 200
