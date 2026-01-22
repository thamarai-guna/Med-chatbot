import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import PatientDashboard from './components/PatientDashboard';
import DoctorDashboard from './components/DoctorDashboard';
import PatientDetail from './components/PatientDetail';

/**
 * Main App Component
 * 
 * Handles:
 * - User authentication state
 * - Routing between different pages
 * - Redirects based on user role
 */
function App() {
  // User state: stores logged-in user info or null
  const [user, setUser] = useState(() => {
    // Try to restore user from localStorage on page load
    const savedUser = localStorage.getItem('user');
    return savedUser ? JSON.parse(savedUser) : null;
  });

  // Handle login - store user and update state
  const handleLogin = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  // Handle logout - clear user and localStorage
  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  return (
    <Router>
      <Routes>
        {/* Public routes - anyone can access */}
        <Route 
          path="/login" 
          element={user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />} 
        />
        <Route 
          path="/register" 
          element={user ? <Navigate to="/" /> : <Register />} 
        />

        {/* Protected routes - redirect to login if not authenticated */}
        
        {/* Patient routes */}
        <Route 
          path="/patient/dashboard" 
          element={user && user.role === 'patient' ? <PatientDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
        />

        {/* Doctor routes */}
        <Route 
          path="/doctor/dashboard" 
          element={user && user.role === 'doctor' ? <DoctorDashboard user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
        />

        <Route 
          path="/doctor/patient/:patientId" 
          element={user && user.role === 'doctor' ? <PatientDetail user={user} onLogout={handleLogout} /> : <Navigate to="/login" />} 
        />

        {/* Root route - redirect based on user role or to login */}
        <Route 
          path="/" 
          element={
            user ? (
              user.role === 'patient' ? <Navigate to="/patient/dashboard" /> : <Navigate to="/doctor/dashboard" />
            ) : (
              <Navigate to="/login" />
            )
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;
