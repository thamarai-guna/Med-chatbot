"""Authentication routes (login, register)."""
from flask import Blueprint, request, jsonify
from models import User

# Create blueprint for auth routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "password123",
        "role": "patient" or "doctor"
    }
    """
    data = request.get_json()
    
    # Validate input
    if not data or not all(k in data for k in ['email', 'password', 'role']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip().lower()
    
    # Validation
    if not email or '@' not in email:
        return jsonify({'error': 'Invalid email'}), 400
    
    if len(password) < 4:
        return jsonify({'error': 'Password must be at least 4 characters'}), 400
    
    if role not in ['patient', 'doctor']:
        return jsonify({'error': 'Role must be "patient" or "doctor"'}), 400
    
    # Try to create user
    user = User.create(email, password, role)
    
    if user is None:
        return jsonify({'error': 'Email already registered'}), 409
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user.
    
    Expected JSON:
    {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    data = request.get_json()
    
    # Validate input
    if not data or not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Missing email or password'}), 400
    
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    # Find user
    user = User.find_by_email(email)
    
    if user is None:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Check password (simple comparison - not production secure!)
    if user['password'] != password:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Return user data (frontend will store this in localStorage/state)
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'email': user['email'],
            'role': user['role']
        }
    }), 200
