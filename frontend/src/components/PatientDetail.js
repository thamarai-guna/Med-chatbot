import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

/**
 * Patient Detail Component
 * 
 * Shows doctor the details of a specific patient
 * Currently shows empty skeleton - will show check-ins, vitals, etc.
 */
function PatientDetail({ user, onLogout }) {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch patient details on mount
  useEffect(() => {
    fetchPatientDetails();
  }, [patientId]);

  const fetchPatientDetails = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/patients/${patientId}`
      );
      setPatient(response.data.patient);
      setError('');
    } catch (err) {
      setError('Failed to load patient details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGoBack = () => {
    navigate('/doctor/dashboard');
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>MedHub - Patient Details</h1>
        <div className="user-info">
          <span>{user.email}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <button onClick={handleGoBack} className="back-btn">
          ← Back to Patients
        </button>

        {loading && <p className="loading-message">Loading patient details...</p>}
        {error && <p className="error-message">{error}</p>}

        {!loading && patient && (
          <div>
            <div className="patient-detail-card">
              <h2>{patient.email}</h2>
              <div className="patient-meta">
                <p><strong>Patient ID:</strong> {patient.id}</p>
                <p><strong>Role:</strong> {patient.role}</p>
              </div>
            </div>

            <div className="checkins-section">
              <h3>Patient Check-ins</h3>
              <p className="placeholder-text">
                Check-in history will appear here once available.
              </p>
            </div>

            <div className="placeholder-section">
              <p className="placeholder-text">
                ✨ More features coming soon! ✨
              </p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default PatientDetail;
