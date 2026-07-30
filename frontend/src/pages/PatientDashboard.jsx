/**
 * Patient Dashboard
 * Refactored with Split-View Layout (Sidebar + Chat)
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
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [activeTab, setActiveTab] = useState('files'); // 'files' or 'chat'

  const navigate = useNavigate();
  // Theme context is still used for toggle, but styles are now CSS vars
  const { theme } = useTheme();

  const patientId = localStorage.getItem('patientId');
  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  useEffect(() => {
    const role = localStorage.getItem('userRole');
    if (role !== 'patient' || !patientId) {
      navigate('/login');
      return;
    }
    loadPatientData();
  }, []);

  const loadPatientData = async () => {
    try {
      const patient = await getPatient(patientId);
      setPatientData(patient);

      const statusResponse = await axios.get(
        `${API_BASE_URL}/api/patient/${patientId}/report/status`
      );
      setReportStatus(statusResponse.data);

      // Auto-switch to chat if reports exist and we haven't manually set a tab yet
      // (Simplified logic: always default to chat if ready, files if not)
      if (statusResponse.data.has_medical_report) {
        setActiveTab('chat');
        const risk = await getRiskSummary(patientId);
        setRiskSummary(risk);
      } else {
        setActiveTab('files');
      }

    } catch (err) {
      console.error('Failed to load patient data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReportUploaded = async () => {
    // Refresh data but don't force switch tab immediately, let user see success message
    const patient = await getPatient(patientId);
    setPatientData(patient);

    const statusResponse = await axios.get(
      `${API_BASE_URL}/api/patient/${patientId}/report/status`
    );
    setReportStatus(statusResponse.data);

    if (statusResponse.data.has_medical_report) {
      const risk = await getRiskSummary(patientId);
      setRiskSummary(risk);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="app-container" style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="text-xl">Loading your dashboard...</div>
        </div>
      </div>
    );
  }

  const hasReport = reportStatus?.has_medical_report;

  return (
    <div className="app-container">
      {/* Sidebar - Persistent Info */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>

        {/* Sidebar Header */}
        <div style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem' }}>🏥</span>
            <h1 className="text-lg" style={{ fontWeight: 700 }}>Medical AI</h1>
          </div>
          <p className="text-sm text-muted">Welcome, {patientData?.name?.split(' ')[0]}</p>
        </div>

        {/* Risk Status Card (Mini) */}
        {hasReport && (
          <div className="card" style={{ marginBottom: '1.5rem', borderLeft: '4px solid var(--pk-accent)' }}>
            <div className="text-xs text-muted" style={{ marginBottom: '0.5rem' }}>CURRENT RISK STATUS</div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <RiskBadge level={riskSummary?.max_risk_level || 'LOW'} size="medium" />
              <span style={{ fontSize: '1.5rem' }}>
                {riskSummary?.max_risk_level === 'CRITICAL' ? '🚨' :
                  riskSummary?.max_risk_level === 'HIGH' ? '⚠️' :
                    riskSummary?.max_risk_level === 'MEDIUM' ? '📋' : '✓'}
              </span>
            </div>
          </div>
        )}

        {/* Navigation / Tabs */}
        <div style={{ flex: 1 }}>
          <div className="text-xs text-muted" style={{ fontWeight: 600, marginBottom: '0.75rem', textTransform: 'uppercase' }}>
            Menu
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>

            {/* File Management Tab */}
            <button
              className={`btn ${activeTab === 'files' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ justifyContent: 'flex-start' }}
              onClick={() => setActiveTab('files')}
            >
              <span style={{ marginRight: '0.5rem' }}>📂</span>
              Medical Records
            </button>

            {/* Chat Assistant Tab */}
            <button
              className={`btn ${activeTab === 'chat' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ justifyContent: 'flex-start', opacity: hasReport ? 1 : 0.5, cursor: hasReport ? 'pointer' : 'not-allowed' }}
              onClick={() => hasReport && setActiveTab('chat')}
              disabled={!hasReport}
              title={!hasReport ? "Upload reports first to unlock chat" : "Open Chat Assistant"}
            >
              <span style={{ marginRight: '0.5rem' }}>💬</span>
              Chat Assistant
              {!hasReport && <span style={{ marginLeft: 'auto', fontSize: '12px' }}>🔒</span>}
            </button>

          </div>
        </div>

        {/* Sidebar Footer */}
        <div style={{ paddingTop: '1rem', borderTop: '1px solid var(--pk-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <span className="text-sm text-muted">Theme</span>
            <ThemeToggle />
          </div>
          <button onClick={handleLogout} className="btn btn-outline" style={{ width: '100%' }}>
            Log Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">

        {/* Mobile Header Toggle */}
        <div className="d-md-none" style={{ padding: '1rem', borderBottom: '1px solid var(--pk-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="text-lg font-bold">Medical Assistant</span>
          <button className="btn btn-ghost" onClick={() => setSidebarOpen(!sidebarOpen)}>☰</button>
        </div>

        {/* Disclaimer Banner */}
        <div style={{ padding: '0.5rem 1rem', background: 'var(--pk-risk-medium-bg)', borderBottom: '1px solid var(--pk-risk-medium-border)', textAlign: 'center', fontSize: '0.8rem', color: 'var(--pk-risk-medium-text)' }}>
          ⚠️ AI Monitor - For educational purposes only. Call emergency services in a crisis.
        </div>

        {/* Content Body */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

          {/* View: Chat Assistant */}
          {activeTab === 'chat' && hasReport && (
            <ChatBox patientId={patientId} />
          )}

          {/* View: File Management */}
          {activeTab === 'files' && (
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '2rem', overflowY: 'auto' }}>
              <div style={{ maxWidth: '800px', width: '100%', margin: '0 auto' }}>
                <div style={{ marginBottom: '2rem' }}>
                  <h2 className="text-xl" style={{ marginBottom: '0.5rem' }}>Manage Records</h2>
                  <p className="text-muted">Upload and manage your medical documents here. The AI uses these to understand your health context.</p>
                </div>

                <ReportUploadComponent
                  patientId={patientId}
                  onReportUploaded={handleReportUploaded}
                />
              </div>
            </div>
          )}

        </div>

      </main>

      {/* Overlay for mobile sidebar */}
      {sidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 40 }}
        />
      )}
    </div>
  );
};

export default PatientDashboard;
