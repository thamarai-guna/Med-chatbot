/**
 * Patient Dashboard
 * Main interface for patients to interact with AI chatbot
 * 
 * MANDATORY FLOW:
 * 1. Check medical report status
 * 2. If no report → Show upload component (BLOCKING)
 * 3. If report exists → Show chat interface (ENABLED)
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';
import ChatBox from '../components/ChatBox';
import RiskBadge from '../components/RiskBadge';
import ReportUploadComponent from '../components/ReportUploadComponent';
import { getPatient, getRiskSummary } from '../api/api';
import axios from 'axios';

const PatientDashboard = () => {
  const [patientData, setPatientData] = useState(null);
  const [riskSummary, setRiskSummary] = useState(null);
  const [reportStatus, setReportStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { theme } = useTheme();

  const patientId = localStorage.getItem('patientId');
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
      // Load patient data
      const patient = await getPatient(patientId);
      setPatientData(patient);

      // Check medical report status (CRITICAL GATE)
      const statusResponse = await axios.get(
        `${API_BASE_URL}/api/patient/${patientId}/report/status`
      );
      setReportStatus(statusResponse.data);

      // Load risk summary only if report exists
      if (statusResponse.data.has_medical_report) {
        const risk = await getRiskSummary(patientId);
        setRiskSummary(risk);
      }
    } catch (err) {
      console.error('Failed to load patient data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReportUploaded = () => {
    // Refresh status and data after report upload
    loadPatientData();
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
    maxWidth: '900px',
    margin: '0 auto',
    width: '100%',
    padding: '24px',
  };

  const disclaimerStyle = {
    backgroundColor: theme.riskMedium.bg,
    border: `1px solid ${theme.riskMedium.border}`,
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '24px',
    fontSize: '14px',
    color: theme.riskMedium.text,
    lineHeight: '1.5',
    transition: 'all 0.3s',
  };

  const sectionStyle = {
    marginBottom: '24px',
  };

  const sectionTitleStyle = {
    fontSize: '16px',
    fontWeight: '600',
    color: theme.text,
    marginBottom: '12px',
    transition: 'color 0.3s',
  };

  const riskStatusStyle = {
    backgroundColor: theme.bgSecondary,
    padding: '20px',
    borderRadius: '12px',
    border: `1px solid ${theme.border}`,
    boxShadow: `0 2px 8px ${theme.shadow}`,
    transition: 'all 0.3s',
  };

  const riskContentStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  };

  const riskTextStyle = {
    flex: 1,
  };

  const riskLabelStyle = {
    fontSize: '13px',
    color: theme.textSecondary,
    marginBottom: '4px',
    transition: 'color 0.3s',
  };

  const riskCountStyle = {
    fontSize: '15px',
    fontWeight: '500',
    color: theme.text,
    transition: 'color 0.3s',
  };

  const chatContainerStyle = {
    backgroundColor: theme.bgSecondary,
    borderRadius: '12px',
    border: `1px solid ${theme.border}`,
    overflow: 'hidden',
    transition: 'all 0.3s',
  };

  const infoGridStyle = {
    backgroundColor: theme.bgSecondary,
    padding: '20px',
    borderRadius: '12px',
    border: `1px solid ${theme.border}`,
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '16px',
    transition: 'all 0.3s',
  };

  const infoCellStyle = {
    display: 'flex',
    flexDirection: 'column',
  };

  const infoLabelStyle = {
    fontSize: '12px',
    color: theme.textSecondary,
    marginBottom: '4px',
    fontWeight: '500',
    transition: 'color 0.3s',
  };

  const infoValueStyle = {
    fontSize: '15px',
    fontWeight: '600',
    color: theme.text,
    transition: 'color 0.3s',
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: theme.bg, transition: 'background-color 0.3s' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: '18px', fontWeight: '500', marginBottom: '12px', color: theme.text }}>Loading your dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      {/* Header */}
      <div style={headerStyle}>
        <div style={headerTitleStyle}>
          <div>
            <div style={{ fontSize: '20px' }}>🏥</div>
          </div>
          <div style={titleStyle}>
            <h1 style={mainTitleStyle}>Medical Assistant</h1>
            <div style={subtitleStyle}>{patientData?.name}</div>
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
        {/* Disclaimer */}
        <div style={disclaimerStyle}>
          <strong>⚠️ Important Disclaimer:</strong> This AI assistant is for monitoring and educational purposes only and does not replace professional medical advice. 
          If you are experiencing a medical emergency, please call emergency services immediately.
        </div>

        {/* Medical Report Upload - MANDATORY GATE BEFORE CHATTING */}
        <ReportUploadComponent 
          patientId={patientId} 
          onReportUploaded={handleReportUploaded}
        />

        {/* Risk Status - Only show if report exists */}
        {reportStatus?.has_medical_report && (
          <div style={sectionStyle}>
            <div style={sectionTitleStyle}>Current Health Status</div>
            <div style={riskStatusStyle}>
              <div style={riskContentStyle}>
                <div style={{ fontSize: '48px' }}>
                  {riskSummary?.max_risk_level === 'CRITICAL' ? '🚨' : 
                   riskSummary?.max_risk_level === 'HIGH' ? '⚠️' : 
                   riskSummary?.max_risk_level === 'MEDIUM' ? '📋' : 
                   '✓'}
                </div>
                <div style={riskTextStyle}>
                  <div style={riskLabelStyle}>Risk Assessment</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                    <RiskBadge level={riskSummary?.max_risk_level || 'LOW'} size="large" />
                    <span style={{ fontSize: '14px', color: theme.textSecondary }}>
                      Based on {riskSummary?.total_queries || 0} conversation{riskSummary?.total_queries !== 1 ? 's' : ''}
                    </span>
                  </div>
                  {riskSummary?.risk_distribution && (
                    <div style={{ fontSize: '12px', color: theme.textSecondary, display: 'flex', gap: '16px' }}>
                      {Object.entries(riskSummary.risk_distribution).map(([level, count]) => (
                        count > 0 && <span key={level}>{level}: {count}</span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chat Interface - Enabled only if report exists */}
        {reportStatus?.has_medical_report && (
          <div style={sectionStyle}>
            <div style={sectionTitleStyle}>Chat with AI Assistant</div>
            <div style={chatContainerStyle}>
              <ChatBox patientId={patientId} />
            </div>
          </div>
        )}

        {/* Patient Info */}
        <div style={sectionStyle}>
          <div style={sectionTitleStyle}>Your Information</div>
          <div style={infoGridStyle}>
            <div style={infoCellStyle}>
              <div style={infoLabelStyle}>Name</div>
              <div style={infoValueStyle}>{patientData?.name}</div>
            </div>
            <div style={infoCellStyle}>
              <div style={infoLabelStyle}>Age</div>
              <div style={infoValueStyle}>{patientData?.age || 'N/A'}</div>
            </div>
            <div style={infoCellStyle}>
              <div style={infoLabelStyle}>Email</div>
              <div style={infoValueStyle}>{patientData?.email || 'N/A'}</div>
            </div>
            <div style={infoCellStyle}>
              <div style={infoLabelStyle}>Patient ID</div>
              <div style={infoValueStyle}>{patientData?.patient_id}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;
