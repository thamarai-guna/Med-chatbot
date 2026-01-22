import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Patient Dashboard Component
 * 
 * Displays patient welcome screen with options
 * For now: empty skeleton with "Start Today's Check-in" button
 */
function PatientDashboard({ user, onLogout }) {
  const navigate = useNavigate();

  const handleStartCheckin = () => {
    // TODO: Implement check-in flow
    alert('Check-in feature coming soon!');
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>MedHub - Patient Dashboard</h1>
        <div className="user-info">
          <span>{user.email}</span>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome, Patient!</h2>
          <p>You are logged in as: <strong>{user.email}</strong></p>
        </div>

        <div className="actions-section">
          <h3>Today's Actions</h3>
          <button 
            onClick={handleStartCheckin}
            className="primary-btn"
          >
            📋 Start Today's Check-in
          </button>
        </div>

        <div className="placeholder-section">
          <p className="placeholder-text">
            ✨ More features coming soon! ✨
          </p>
        </div>
      </main>
    </div>
  );
}

export default PatientDashboard;
