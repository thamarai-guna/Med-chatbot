/**
 * Login Page
 * Simple role selection for demo purposes
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAllPatients } from '../api/api';

const Login = () => {
  const [role, setRole] = useState('');
  const [patientId, setPatientId] = useState('');
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Load patients when patient role is selected
  const handleRoleChange = async (selectedRole) => {
    setRole(selectedRole);
    setError(null);

    if (selectedRole === 'patient') {
      setLoading(true);
      try {
        const data = await getAllPatients();
        setPatients(data.patients || []);
      } catch (err) {
        setError('Failed to load patients: ' + err.message);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleLogin = () => {
    if (!role) {
      setError('Please select a role');
      return;
    }

    if (role === 'patient' && !patientId) {
      setError('Please select a patient');
      return;
    }

    // Store in localStorage for demo
    localStorage.setItem('userRole', role);
    if (role === 'patient') {
      localStorage.setItem('patientId', patientId);
    }

    // Navigate based on role
    navigate(role === 'patient' ? '/patient' : '/doctor');
  };

  const containerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f8f9fa',
  };

  const cardStyle = {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    width: '400px',
  };

  const titleStyle = {
    fontSize: '24px',
    fontWeight: 'bold',
    marginBottom: '8px',
    textAlign: 'center',
  };

  const subtitleStyle = {
    fontSize: '14px',
    color: '#6c757d',
    marginBottom: '32px',
    textAlign: 'center',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '8px',
    fontWeight: 'bold',
    fontSize: '14px',
  };

  const selectStyle = {
    width: '100%',
    padding: '12px',
    marginBottom: '16px',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '14px',
  };

  const buttonStyle = {
    width: '100%',
    padding: '12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
  };

  const errorStyle = {
    color: '#dc3545',
    backgroundColor: '#f8d7da',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '16px',
    fontSize: '14px',
  };

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h1 style={titleStyle}>🏥 Medical Chatbot</h1>
        <p style={subtitleStyle}>AI-Powered Patient Monitoring System</p>

        {error && <div style={errorStyle}>{error}</div>}

        <label style={labelStyle}>Select Role</label>
        <select
          value={role}
          onChange={(e) => handleRoleChange(e.target.value)}
          style={selectStyle}
        >
          <option value="">-- Choose Role --</option>
          <option value="patient">Patient</option>
          <option value="doctor">Doctor</option>
        </select>

        {role === 'patient' && (
          <>
            <label style={labelStyle}>Select Patient</label>
            {loading ? (
              <div style={{ textAlign: 'center', padding: '12px', color: '#6c757d' }}>
                Loading patients...
              </div>
            ) : (
              <select
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                style={selectStyle}
              >
                <option value="">-- Choose Patient --</option>
                {patients.map((patient) => (
                  <option key={patient.patient_id} value={patient.patient_id}>
                    {patient.name} ({patient.patient_id})
                  </option>
                ))}
              </select>
            )}
          </>
        )}

        <button onClick={handleLogin} style={buttonStyle}>
          Login
        </button>

        <div style={{ marginTop: '24px', padding: '12px', backgroundColor: '#e7f3ff', borderRadius: '4px', fontSize: '12px' }}>
          <strong>Demo Mode:</strong> No authentication required. Select a role to continue.
        </div>
      </div>
    </div>
  );
};

export default Login;
