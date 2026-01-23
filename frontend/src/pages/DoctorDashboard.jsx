/**
 * Doctor Dashboard
 * Interface for doctors to monitor patients and view alerts
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';
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
  const { theme } = useTheme();

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
    backgroundColor: theme.bg,
    display: 'flex',
    flexDirection: 'column',
    transition: 'background-color 0.3s',
  };

  const headerStyle = {
    backgroundColor: theme.bgSecondary,
    borderBottom: `1px solid ${theme.border}`,
    padding: '20px 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: `0 1px 3px ${theme.shadow}`,
    transition: 'all 0.3s',
  };

  const headerTitleStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  };

  const titleStyle = {
    display: 'flex',
    flexDirection: 'column',
  };

  const mainTitleStyle = {
    margin: 0,
    fontSize: '22px',
    fontWeight: '600',
    color: theme.text,
    transition: 'color 0.3s',
  };

  const subtitleStyle = {
    fontSize: '13px',
    marginTop: '4px',
    color: theme.textSecondary,
    transition: 'color 0.3s',
  };

  const headerControlsStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  };

  const logoutButtonStyle = {
    padding: '8px 16px',
    backgroundColor: theme.bgTertiary,
    color: theme.text,
    border: `1px solid ${theme.border}`,
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: '500',
    fontSize: '14px',
    transition: 'all 0.2s',
  };

  const contentStyle = {
    flex: 1,
    maxWidth: '1400px',
    margin: '0 auto',
    width: '100%',
    padding: '24px',
  };

  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: '320px 1fr',
    gap: '24px',
  };

  const cardStyle = {
    backgroundColor: theme.bgSecondary,
    padding: '20px',
    borderRadius: '12px',
    border: `1px solid ${theme.border}`,
    boxShadow: `0 2px 8px ${theme.shadow}`,
    transition: 'all 0.3s',
  };

  const patientListStyle = {
    maxHeight: '500px',
    overflowY: 'auto',
  };

  const patientItemStyle = (isSelected) => ({
    padding: '12px',
    cursor: 'pointer',
    borderRadius: '8px',
    marginBottom: '8px',
    backgroundColor: isSelected ? theme.accentLight : 'transparent',
    border: isSelected ? `2px solid ${theme.accent}` : `1px solid ${theme.border}`,
    transition: 'all 0.2s',
  });

  const emptyStateStyle = {
    textAlign: 'center',
    padding: '60px 20px',
    color: theme.textSecondary,
    transition: 'color 0.3s',
  };

  const riskGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    marginTop: '12px',
  };

  const riskStatStyle = {
    padding: '12px',
    backgroundColor: theme.bgTertiary,
    borderRadius: '8px',
    textAlign: 'center',
    transition: 'background-color 0.3s',
  };

  const riskLabelStyle = {
    fontSize: '12px',
    color: theme.textSecondary,
    marginBottom: '8px',
    fontWeight: '500',
    transition: 'color 0.3s',
  };

  const riskValueStyle = {
    fontSize: '24px',
    fontWeight: '700',
    color: theme.text,
    transition: 'color 0.3s',
  };

  const conversationItemStyle = {
    padding: '12px',
    borderBottom: `1px solid ${theme.border}`,
    marginBottom: '12px',
    transition: 'border-color 0.3s',
  };

  const conversationQStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '8px',
  };

  const conversationQTextStyle = {
    fontWeight: '600',
    fontSize: '14px',
    color: theme.text,
    flex: 1,
    marginRight: '8px',
    transition: 'color 0.3s',
  };

  const conversationAStyle = {
    fontSize: '14px',
    color: theme.textSecondary,
    marginBottom: '8px',
    lineHeight: '1.4',
    transition: 'color 0.3s',
  };

  const conversationReasonStyle = {
    fontSize: '12px',
    color: theme.textTertiary,
    fontStyle: 'italic',
    marginBottom: '4px',
    transition: 'color 0.3s',
  };

  const conversationTimeStyle = {
    fontSize: '12px',
    color: theme.textTertiary,
    transition: 'color 0.3s',
  };

  const patientNameStyle = {
    fontWeight: '600',
    fontSize: '14px',
    color: theme.text,
    transition: 'color 0.3s',
  };

  const patientIdStyle = {
    fontSize: '12px',
    color: theme.textSecondary,
    marginTop: '4px',
    transition: 'color 0.3s',
  };

  if (loading && patients.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: theme.bg, transition: 'background-color 0.3s' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '18px', fontWeight: '500', marginBottom: '12px', color: theme.text }}>Loading patients...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div style={headerTitleStyle}>
          <div style={{ fontSize: '20px' }}>👨‍⚕️</div>
          <div style={titleStyle}>
            <h1 style={mainTitleStyle}>Doctor Dashboard</h1>
            <div style={subtitleStyle}>Patient Monitoring System</div>
          </div>
        </div>
        <div style={headerControlsStyle}>
          <ThemeToggle />
          <button onClick={handleLogout} style={logoutButtonStyle}>
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
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
              <h3 style={{ margin: '0 0 16px 0', fontSize: '15px', fontWeight: '600', color: theme.text, transition: 'color 0.3s' }}>
                Patients ({patients.length})
              </h3>
              <div style={patientListStyle}>
                {patients.map((patient) => (
                  <div
                    key={patient.patient_id}
                    onClick={() => handlePatientSelect(patient.patient_id)}
                    style={patientItemStyle(selectedPatient === patient.patient_id)}
                  >
                    <div style={patientNameStyle}>
                      {patient.name}
                    </div>
                    <div style={patientIdStyle}>
                      {patient.patient_id}
                    </div>
                    {patient.email && (
                      <div style={patientIdStyle}>
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
                <div style={emptyStateStyle}>
                  <div style={{ fontSize: '48px', marginBottom: '16px' }}>👈</div>
                  <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px', color: theme.text, transition: 'color 0.3s' }}>
                    Select a patient
                  </div>
                  <div>Choose a patient from the list to view their details</div>
                </div>
              </div>
            ) : (
              <>
                {/* Patient Info & Risk */}
                <div style={cardStyle}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h2 style={{ margin: '0 0 8px 0', fontSize: '20px', fontWeight: '600', color: theme.text, transition: 'color 0.3s' }}>
                        {selectedPatientData?.name}
                      </h2>
                      <div style={{ fontSize: '13px', color: theme.textSecondary, transition: 'color 0.3s' }}>
                        ID: {selectedPatientData?.patient_id}
                      </div>
                      {selectedPatientData?.age && (
                        <div style={{ fontSize: '13px', color: theme.textSecondary, transition: 'color 0.3s' }}>
                          Age: {selectedPatientData.age} years
                        </div>
                      )}
                      {selectedPatientData?.email && (
                        <div style={{ fontSize: '13px', color: theme.textSecondary, transition: 'color 0.3s' }}>
                          {selectedPatientData.email}
                        </div>
                      )}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '12px', color: theme.textSecondary, marginBottom: '8px', fontWeight: '500', transition: 'color 0.3s' }}>
                        Current Risk Level
                      </div>
                      <RiskBadge level={riskSummary?.max_risk_level || 'LOW'} size="large" />
                    </div>
                  </div>
                </div>

                {/* Risk Summary */}
                {riskSummary && (
                  <div style={cardStyle}>
                    <h3 style={{ margin: '0 0 16px 0', fontSize: '15px', fontWeight: '600', color: theme.text, transition: 'color 0.3s' }}>
                      Risk Summary (Last 30 Days)
                    </h3>
                    <div style={riskGridStyle}>
                      <div style={riskStatStyle}>
                        <div style={riskLabelStyle}>Total Queries</div>
                        <div style={riskValueStyle}>{riskSummary.total_queries}</div>
                      </div>
                      <div style={riskStatStyle}>
                        <div style={riskLabelStyle}>Low Risk</div>
                        <div style={{ ...riskValueStyle, color: theme.accent }}>
                          {riskSummary.risk_distribution?.LOW || 0}
                        </div>
                      </div>
                      <div style={riskStatStyle}>
                        <div style={riskLabelStyle}>Medium/High</div>
                        <div style={{ ...riskValueStyle, color: theme.riskHigh.text }}>
                          {(riskSummary.risk_distribution?.MEDIUM || 0) + (riskSummary.risk_distribution?.HIGH || 0)}
                        </div>
                      </div>
                      <div style={riskStatStyle}>
                        <div style={riskLabelStyle}>Critical</div>
                        <div style={{ ...riskValueStyle, color: theme.riskCritical.text }}>
                          {riskSummary.risk_distribution?.CRITICAL || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Recent Conversations */}
                {chatHistory && chatHistory.history && chatHistory.history.length > 0 && (
                  <div style={cardStyle}>
                    <h3 style={{ margin: '0 0 16px 0', fontSize: '15px', fontWeight: '600', color: theme.text, transition: 'color 0.3s' }}>
                      Recent Conversations (Last 10)
                    </h3>
                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                      {chatHistory.history.map((item, idx) => (
                        <div key={idx} style={conversationItemStyle}>
                          <div style={conversationQStyle}>
                            <div style={conversationQTextStyle}>Q: {item.question}</div>
                            <RiskBadge level={item.risk_level} size="small" />
                          </div>
                          <div style={conversationAStyle}>
                            A: {item.answer.substring(0, 150)}...
                          </div>
                          {item.risk_reason && (
                            <div style={conversationReasonStyle}>
                              {item.risk_reason}
                            </div>
                          )}
                          <div style={conversationTimeStyle}>
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
