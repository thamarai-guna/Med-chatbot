/**
 * Login Page
 * Username and password authentication
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

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

  const inputStyle = {
    width: '100%',
    padding: '12px',
    marginBottom: '16px',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '14px',
    boxSizing: 'border-box',
  };

  const buttonStyle = {
    width: '100%',
    padding: '12px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: loading ? 'not-allowed' : 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
    opacity: loading ? 0.6 : 1,
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
        <p style={subtitleStyle}>Post-Discharge Neurological Monitoring</p>

        {error && <div style={errorStyle}>{error}</div>}

        <label style={labelStyle}>Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          placeholder="Enter your username"
          style={inputStyle}
          disabled={loading}
        />

        <label style={labelStyle}>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
          placeholder="Enter your password"
          style={inputStyle}
          disabled={loading}
        />

        <button onClick={handleLogin} disabled={loading} style={buttonStyle}>
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <div style={{ marginTop: '24px', padding: '12px', backgroundColor: '#e7f3ff', borderRadius: '4px', fontSize: '12px' }}>
          <strong>Demo Credentials:</strong>
          <div style={{ marginTop: '8px' }}>
            Patient: patient1 / pass123<br/>
            Doctor: doctor1 / pass123<br/>
            Nurse: nurse1 / pass123
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
