/**
 * Doctor Dashboard
 * Interface for doctors to monitor patients and view alerts
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import RiskBadge from '../components/RiskBadge';
import AlertList from '../components/AlertList';
import { getAllPatients, getPatient, getRiskSummary, getChatHistory } from '../api/api';

const DoctorDashboard = () => {
  const [patients, setPatients] = useState([]);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [selectedPatientData, setSelectedPatientData] = useState(null);
  const [riskSummary, setRiskSummary] = useState(null);
  const [chatHistory, setChatHistory] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if logged in
    const role = localStorage.getItem('userRole');
    if (role !== 'doctor') {
      navigate('/login');
      return;
    }

    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      const data = await getAllPatients();
      setPatients(data.patients || []);
      
      // Generate alerts for high-risk patients
      const highRiskAlerts = [];
      for (const patient of data.patients || []) {
        try {
          const risk = await getRiskSummary(patient.patient_id);
          if (risk.max_risk_level === 'HIGH' || risk.max_risk_level === 'CRITICAL') {
            highRiskAlerts.push({
              patient_id: patient.patient_id,
              patient_name: patient.name,
              risk_level: risk.max_risk_level,
              reason: `Patient has ${risk.max_risk_level} risk based on recent conversations`,
              timestamp: new Date().toISOString(),
            });
          }
        } catch (err) {
          console.error(`Failed to get risk for patient ${patient.patient_id}:`, err);
        }
      }
      setAlerts(highRiskAlerts);
    } catch (err) {
      console.error('Failed to load patients:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePatientSelect = async (patientId) => {
    if (!patientId) {
      setSelectedPatient(null);
      setSelectedPatientData(null);
      setRiskSummary(null);
      setChatHistory(null);
      return;
    }

    setSelectedPatient(patientId);
    setLoading(true);

    try {
      const [patient, risk, history] = await Promise.all([
        getPatient(patientId),
        getRiskSummary(patientId),
        getChatHistory(patientId, 10), // Last 10 messages
      ]);
      setSelectedPatientData(patient);
      setRiskSummary(risk);
      setChatHistory(history);
    } catch (err) {
      console.error('Failed to load patient details:', err);
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
    backgroundColor: '#28a745',
    color: 'white',
    padding: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  };

  const contentStyle = {
    maxWidth: '1400px',
    margin: '0 auto',
    padding: '24px',
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: '350px 1fr',
    gap: '24px',
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
    color: '#28a745',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontWeight: 'bold',
  };

  const patientListStyle = {
    maxHeight: '400px',
    overflowY: 'auto',
  };

  const patientItemStyle = (isSelected) => ({
    padding: '12px',
    cursor: 'pointer',
    borderRadius: '4px',
    marginBottom: '8px',
    backgroundColor: isSelected ? '#e7f3ff' : 'transparent',
    border: isSelected ? '2px solid #007bff' : '1px solid #dee2e6',
  });

  if (loading && patients.length === 0) {
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
          <h1 style={{ margin: 0, fontSize: '24px' }}>Doctor Dashboard</h1>
          <div style={{ fontSize: '14px', marginTop: '4px', opacity: 0.9 }}>
            Patient Monitoring System
          </div>
        </div>
        <button onClick={handleLogout} style={buttonStyle}>
          Logout
        </button>
      </div>

      <div style={contentStyle}>
        <div style={gridStyle}>
          {/* Left Sidebar */}
          <div>
            {/* Alerts */}
            <div style={{ marginBottom: '24px' }}>
              <AlertList alerts={alerts} />
            </div>

            {/* Patient List */}
            <div style={cardStyle}>
              <h2 style={{ marginTop: 0, marginBottom: '16px' }}>
                Patients ({patients.length})
              </h2>
              <div style={patientListStyle}>
                {patients.map((patient) => (
                  <div
                    key={patient.patient_id}
                    onClick={() => handlePatientSelect(patient.patient_id)}
                    style={patientItemStyle(selectedPatient === patient.patient_id)}
                  >
                    <div style={{ fontWeight: 'bold' }}>{patient.name}</div>
                    <div style={{ fontSize: '12px', color: '#6c757d', marginTop: '4px' }}>
                      ID: {patient.patient_id}
                    </div>
                    {patient.email && (
                      <div style={{ fontSize: '12px', color: '#6c757d' }}>
                        {patient.email}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div>
            {!selectedPatient ? (
              <div style={cardStyle}>
                <div style={{ textAlign: 'center', padding: '40px', color: '#6c757d' }}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>👈</div>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
                    Select a patient
                  </div>
                  <div>Choose a patient from the list to view their details</div>
                </div>
              </div>
            ) : (
              <>
                {/* Patient Info & Risk */}
                <div style={cardStyle}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div>
                      <h2 style={{ margin: 0, marginBottom: '8px' }}>
                        {selectedPatientData?.name}
                      </h2>
                      <div style={{ fontSize: '14px', color: '#6c757d' }}>
                        ID: {selectedPatientData?.patient_id}
                      </div>
                      {selectedPatientData?.age && (
                        <div style={{ fontSize: '14px', color: '#6c757d' }}>
                          Age: {selectedPatientData.age}
                        </div>
                      )}
                      {selectedPatientData?.email && (
                        <div style={{ fontSize: '14px', color: '#6c757d' }}>
                          Email: {selectedPatientData.email}
                        </div>
                      )}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '8px' }}>
                        Current Risk Level
                      </div>
                      <RiskBadge level={riskSummary?.max_risk_level || 'LOW'} size="large" />
                    </div>
                  </div>
                </div>

                {/* Risk Summary */}
                {riskSummary && (
                  <div style={cardStyle}>
                    <h3 style={{ marginTop: 0, marginBottom: '16px' }}>Risk Summary (Last 30 Days)</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                      <div>
                        <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Total Queries</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold' }}>
                          {riskSummary.total_queries}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Low Risk</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                          {riskSummary.risk_distribution?.LOW || 0}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Medium/High</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff6b6b' }}>
                          {(riskSummary.risk_distribution?.MEDIUM || 0) + (riskSummary.risk_distribution?.HIGH || 0)}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '12px', color: '#6c757d', marginBottom: '4px' }}>Critical</div>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
                          {riskSummary.risk_distribution?.CRITICAL || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Recent Conversations */}
                {chatHistory && chatHistory.history && chatHistory.history.length > 0 && (
                  <div style={cardStyle}>
                    <h3 style={{ marginTop: 0, marginBottom: '16px' }}>
                      Recent Conversations (Last 10)
                    </h3>
                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                      {chatHistory.history.map((item, idx) => (
                        <div key={idx} style={{ 
                          padding: '12px', 
                          borderBottom: '1px solid #dee2e6',
                          marginBottom: '12px'
                        }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '8px' }}>
                            <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                              Q: {item.question}
                            </div>
                            <RiskBadge level={item.risk_level} size="small" />
                          </div>
                          <div style={{ fontSize: '14px', color: '#495057', marginBottom: '8px' }}>
                            A: {item.answer.substring(0, 200)}...
                          </div>
                          {item.risk_reason && (
                            <div style={{ fontSize: '12px', color: '#6c757d', fontStyle: 'italic' }}>
                              Risk Reason: {item.risk_reason}
                            </div>
                          )}
                          <div style={{ fontSize: '12px', color: '#6c757d', marginTop: '4px' }}>
                            {new Date(item.timestamp).toLocaleString()}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DoctorDashboard;
