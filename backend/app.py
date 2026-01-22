"""Flask application entry point."""
from flask import Flask
from flask_cors import CORS
from database import init_db
from routes.auth import auth_bp
from routes.patient import patient_bp

# Create Flask app
app = Flask(__name__)

# Enable CORS (allow requests from frontend)
CORS(app)

# Initialize database on startup
init_db()

# Register blueprints (route groups)
app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)

# Simple health check endpoint
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    # Run Flask development server
    # Backend will be at http://localhost:5000
    app.run(debug=True, port=5000)
