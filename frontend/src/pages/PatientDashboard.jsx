/**
 * Patient Dashboard
 * Main interface for patients to interact with AI chatbot
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatBox from '../components/ChatBox';
import RiskBadge from '../components/RiskBadge';
import { getPatient, getRiskSummary } from '../api/api';

const PatientDashboard = () => {
  const [patientData, setPatientData] = useState(null);
  const [riskSummary, setRiskSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const patientId = localStorage.getItem('patientId');

  useEffect(() => {
    // Check if logged in
    const role = localStorage.getItem('userRole');
    if (role !== 'patient' || !patientId) {
      navigate('/login');
      return;
    }

    loadPatientData();
  }, []);

  const loadPatientData = async () => {
    try {
      const [patient, risk] = await Promise.all([
        getPatient(patientId),
        getRiskSummary(patientId),
      ]);
      setPatientData(patient);
      setRiskSummary(risk);
    } catch (err) {
      console.error('Failed to load patient data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  const containerStyle = {
    minHeight: '100vh',
    backgroundColor: '#f8f9fa',
  };

  const headerStyle = {
    backgroundColor: '#007bff',
    color: 'white',
    padding: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  };

  const contentStyle = {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px',
  };

  const cardStyle = {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '8px',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    marginBottom: '24px',
  };

  const buttonStyle = {
    padding: '10px 20px',
    backgroundColor: 'white',
    color: '#007bff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
  };

  const disclaimerStyle = {
    backgroundColor: '#fff3cd',
    border: '1px solid #ffc107',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
    fontSize: '14px',
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        Loading...
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px' }}>Patient Dashboard</h1>
          <div style={{ fontSize: '14px', marginTop: '4px', opacity: 0.9 }}>
            {patientData?.name} (ID: {patientId})
          </div>
        </div>
        <button onClick={handleLogout} style={buttonStyle}>
          Logout
        </button>
      </div>

      <div style={contentStyle}>
        {/* Disclaimer */}
        <div style={disclaimerStyle}>
          <strong>⚠️ Important:</strong> This AI assistant is for monitoring only and does not replace medical advice. 
          If you are experiencing a medical emergency, please call emergency services immediately.
        </div>

        {/* Risk Status */}
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, marginBottom: '16px' }}>Current Risk Status</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <RiskBadge level={riskSummary?.max_risk_level || 'LOW'} size="large" />
            <div>
              <div style={{ fontSize: '14px', color: '#6c757d' }}>
                Based on {riskSummary?.total_queries || 0} recent conversations
              </div>
              {riskSummary?.risk_distribution && (
                <div style={{ fontSize: '12px', color: '#6c757d', marginTop: '4px' }}>
                  Distribution: 
                  {Object.entries(riskSummary.risk_distribution).map(([level, count]) => (
                    count > 0 && <span key={level} style={{ marginLeft: '8px' }}>{level}: {count}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Chat Interface */}
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, marginBottom: '16px' }}>Chat with AI Medical Assistant</h2>
          <ChatBox patientId={patientId} />
        </div>

        {/* Patient Info */}
        <div style={cardStyle}>
          <h2 style={{ marginTop: 0, marginBottom: '16px' }}>Your Information</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
            <div>
              <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Name</div>
              <div style={{ fontWeight: 'bold' }}>{patientData?.name}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Age</div>
              <div style={{ fontWeight: 'bold' }}>{patientData?.age || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Email</div>
              <div style={{ fontWeight: 'bold' }}>{patientData?.email || 'N/A'}</div>
            </div>
            <div>
              <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Patient ID</div>
              <div style={{ fontWeight: 'bold' }}>{patientData?.patient_id}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;
