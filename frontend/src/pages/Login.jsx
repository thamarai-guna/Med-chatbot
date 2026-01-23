/**
 * Login Page
 * Username and password authentication
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';
import ThemeToggle from '../components/ThemeToggle';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { theme } = useTheme();

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      setError('Please enter both username and password');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: username.trim(),
          password: password.trim(),
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();

      // Store authentication data
      localStorage.setItem('userRole', data.role);
      localStorage.setItem('userId', data.user_id);
      if (data.role === 'patient') {
        localStorage.setItem('patientId', data.user_id);
      }

      // Redirect based on role
      if (data.role === 'patient') {
        navigate('/patient');
      } else if (data.role === 'doctor') {
        navigate('/doctor');
      } else if (data.role === 'nurse') {
        navigate('/nurse');
      }
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const containerStyle = {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: theme.bg,
    transition: 'background-color 0.3s',
    position: 'relative',
  };

  const toggleStyle = {
    position: 'absolute',
    top: '20px',
    right: '20px',
  };

  const cardStyle = {
    backgroundColor: theme.bgSecondary,
    padding: '48px',
    borderRadius: '12px',
    boxShadow: `0 10px 25px ${theme.shadowLg}`,
    width: '100%',
    maxWidth: '420px',
    border: `1px solid ${theme.border}`,
    transition: 'all 0.3s',
  };

  const titleStyle = {
    fontSize: '28px',
    fontWeight: '700',
    marginBottom: '8px',
    textAlign: 'center',
    color: theme.text,
    transition: 'color 0.3s',
  };

  const subtitleStyle = {
    fontSize: '14px',
    color: theme.textSecondary,
    marginBottom: '32px',
    textAlign: 'center',
    fontWeight: '500',
    transition: 'color 0.3s',
  };

  const labelStyle = {
    display: 'block',
    marginBottom: '8px',
    fontWeight: '600',
    fontSize: '14px',
    color: theme.text,
    transition: 'color 0.3s',
  };

  const inputStyle = {
    width: '100%',
    padding: '12px 14px',
    marginBottom: '16px',
    border: `1px solid ${theme.border}`,
    borderRadius: '8px',
    fontSize: '15px',
    boxSizing: 'border-box',
    backgroundColor: theme.bg,
    color: theme.text,
    transition: 'all 0.3s',
  };

  const buttonStyle = {
    width: '100%',
    padding: '12px 16px',
    backgroundColor: loading ? theme.borderLight : theme.accent,
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: loading ? 'not-allowed' : 'pointer',
    fontSize: '15px',
    fontWeight: '600',
    opacity: loading ? 0.7 : 1,
    transition: 'background-color 0.2s',
  };

  const errorStyle = {
    color: theme.isDark ? '#fecaca' : '#7f1d1d',
    backgroundColor: theme.riskCritical.bg,
    padding: '12px 14px',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '14px',
    border: `1px solid ${theme.riskCritical.border}`,
    transition: 'all 0.3s',
  };

  const demoBoxStyle = {
    marginTop: '24px',
    padding: '14px',
    backgroundColor: theme.accentLight,
    borderRadius: '8px',
    fontSize: '13px',
    border: `1px solid ${theme.accent}`,
    color: theme.text,
    lineHeight: '1.6',
    transition: 'all 0.3s',
  };

  const demoLabelStyle = {
    fontWeight: '600',
    marginBottom: '8px',
  };

  return (
    <div style={containerStyle}>
      <div style={toggleStyle}>
        <ThemeToggle />
      </div>
      <div style={cardStyle}>
        <h1 style={titleStyle}>🏥 Medical Assistant</h1>
        <p style={subtitleStyle}>Post-Discharge Monitoring System</p>

        {error && <div style={errorStyle}>{error}</div>}

        <label style={labelStyle}>Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          placeholder="Enter username"
          style={inputStyle}
          disabled={loading}
        />

        <label style={labelStyle}>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          placeholder="Enter password"
          style={inputStyle}
          disabled={loading}
        />

        <button onClick={handleLogin} disabled={loading} style={buttonStyle}>
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <div style={demoBoxStyle}>
          <div style={demoLabelStyle}>Demo Credentials:</div>
          <div>
            👤 Patient: patient1 / pass123<br/>
            👨‍⚕️ Doctor: doctor1 / pass123
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
