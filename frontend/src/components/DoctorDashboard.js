import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

/**
 * Doctor Dashboard Component
 * 
 * Displays list of patients for the doctor to view
 * Clicking a patient shows their details page
 */
function DoctorDashboard({ user, onLogout }) {
  const navigate = useNavigate();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Fetch patients list on component mount
  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/patients`);
      setPatients(response.data.patients);
      setError('');
    } catch (err) {
      setError('Failed to load patients list');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewPatient = (patientId) => {
    navigate(`/doctor/patient/${patientId}`);
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>MedHub - Doctor Dashboard</h1>
        <div className="user-info">
          <span>{user.email}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome, Doctor!</h2>
          <p>Managing patients and their health data</p>
        </div>

        <div className="patients-section">
          <h3>Your Patients</h3>

          {loading && <p className="loading-message">Loading patients...</p>}
          {error && <p className="error-message">{error}</p>}

          {!loading && patients.length === 0 && (
            <p className="empty-message">No patients registered yet.</p>
          )}

          {!loading && patients.length > 0 && (
            <div className="patients-list">
              {patients.map((patient) => (
                <div
                  key={patient.id}
                  className="patient-card"
                  onClick={() => handleViewPatient(patient.id)}
                >
                  <div className="patient-info">
                    <h4>{patient.email}</h4>
                    <p>Patient ID: {patient.id}</p>
                  </div>
                  <button className="view-btn">
                    View Details →
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default DoctorDashboard;
