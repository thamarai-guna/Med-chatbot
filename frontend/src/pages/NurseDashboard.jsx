import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getNursePatients } from '../services/api';
import AlertsPanel from '../components/common/AlertsPanel';
import './NurseDashboard.css';

const NurseDashboard = () => {
  const { user, logout } = useAuth();
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSection, setShowSection] = useState('alerts');

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      const response = await getNursePatients();
      setPatients(response.data);
    } catch (err) {
      console.error('Failed to fetch patients:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <h1>🏥 Med-Chatbot</h1>
          <span className="nav-role">Nurse Dashboard</span>
        </div>
        <div className="nav-user">
          <span>👩‍⚕️ {user?.full_name}</span>
          <button onClick={logout} className="btn-logout">Logout</button>
        </div>
      </nav>

      <div className="dashboard-content">
        <div className="dashboard-tabs">
          <button
            className={showSection === 'alerts' ? 'tab-btn active' : 'tab-btn'}
            onClick={() => setShowSection('alerts')}
          >
            🚨 Active Alerts
          </button>
          <button
            className={showSection === 'patients' ? 'tab-btn active' : 'tab-btn'}
            onClick={() => setShowSection('patients')}
          >
            👥 Ward Patients
          </button>
        </div>

        {showSection === 'alerts' && (
          <AlertsPanel userRole="nurse" />
        )}

        {showSection === 'patients' && (
          <div className="patients-section">
            <h2>Ward Patients</h2>
            {loading ? (
              <p>Loading patients...</p>
            ) : patients.length === 0 ? (
              <p>No patients in your ward yet.</p>
            ) : (
              <div className="patients-grid">
                {patients.map((patient) => (
                  <div key={patient.id} className="patient-card">
                    <h3>{patient.full_name}</h3>
                    <p><strong>Patient #:</strong> {patient.patient_number}</p>
                    <p><strong>Ward:</strong> {patient.ward}</p>
                    <p><strong>Bed:</strong> {patient.bed_number}</p>
                    <p><strong>Gender:</strong> {patient.gender}</p>
                    <p><strong>Status:</strong> {patient.is_discharged ? 'Discharged' : 'Active'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default NurseDashboard;
