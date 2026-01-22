import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Auth APIs
export const login = (email, password) => 
  api.post('/auth/login', { email, password });

export const register = (data) => 
  api.post('/auth/register', data);

export const getCurrentUser = () => 
  api.get('/auth/me');

// Alert APIs
export const getAlerts = (statusFilter = null) => {
  const params = statusFilter ? { status_filter: statusFilter } : {};
  return api.get('/alerts', { params });
};

export const acknowledgeAlert = (alertId) => 
  api.post(`/alerts/${alertId}/acknowledge`);

// Doctor APIs
export const getDoctorPatients = () => 
  api.get('/doctor/patients');

export const getPatientDetails = (patientId) => 
  api.get(`/doctor/patients/${patientId}`);

// Nurse APIs
export const getNursePatients = () => 
  api.get('/nurse/patients');

// Patient APIs
export const getPatientProfile = () => 
  api.get('/patient/profile');

// Admin APIs
export const getAllUsers = () => 
  api.get('/admin/users');

export const createPatient = (data) => 
  api.post('/admin/patients', data);

export default api;
