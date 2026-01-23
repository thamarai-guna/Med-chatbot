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
    loadPatientData();
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

        {/* Navigation / Steps */}
        <div style={{ flex: 1 }}>
          <div className="text-xs text-muted" style={{ fontWeight: 600, marginBottom: '0.75rem', textTransform: 'uppercase' }}>
            Checklist
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div className={`btn ${hasReport ? 'btn-ghost' : 'btn-primary'}`} style={{ justifyContent: 'flex-start', opacity: hasReport ? 0.8 : 1 }}>
               <span style={{ marginRight: '0.5rem' }}>{hasReport ? '✅' : '1️⃣'}</span>
               Import Records
            </div>
            <div className={`btn ${hasReport ? 'btn-primary' : 'btn-ghost'}`} style={{ justifyContent: 'flex-start', opacity: hasReport ? 1 : 0.5 }}>
               <span style={{ marginRight: '0.5rem' }}>{hasReport ? '2️⃣' : '🔒'}</span>
               Chat Assistant
            </div>
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

      {/* Main Content Area - Chat First */}
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
          {hasReport ? (
             /* Chat takes full remaining height */
             <ChatBox patientId={patientId} />
          ) : (
             /* Empty State / Upload Gate */
             <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
                <div style={{ maxWidth: '500px', width: '100%' }}>
                   <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                      <div style={{ fontSize: '4rem', marginBottom: '1rem' }}>📂</div>
                      <h2 className="text-xl" style={{ marginBottom: '0.5rem' }}>Upload Medical Records</h2>
                      <p className="text-muted">To ensure the AI gives safe and relevant monitoring advice, please upload your hospital discharge or medical report PDF.</p>
                   </div>
                   
                   <div className="card">
                      <ReportUploadComponent 
                        patientId={patientId} 
                        onReportUploaded={handleReportUploaded}
                      />
                   </div>
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
