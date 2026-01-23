/**
 * API Integration Layer
 * All backend API calls centralized here
 */

import axios from 'axios';

// Base URL - configurable for different environments
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds for chat queries
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.message || error.message || 'An error occurred';
    console.error('API Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

// ============================================================================
// HEALTH & INFO
// ============================================================================

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// ============================================================================
// PATIENT MANAGEMENT
// ============================================================================

export const registerPatient = async (patientData) => {
  const response = await api.post('/api/patient/register', patientData);
  return response.data;
};

export const getPatient = async (patientId) => {
  const response = await api.get(`/api/patient/${patientId}`);
  return response.data;
};

export const getAllPatients = async () => {
  const response = await api.get('/api/patient');
  return response.data;
};

// ============================================================================
// CHAT / RAG
// ============================================================================

export const sendChatMessage = async (patientId, message, vectorStoreName = 'DefaultVectorDB') => {
  const response = await api.post('/api/chat/query', {
    patient_id: patientId,
    message: message,
    vector_store_name: vectorStoreName,
  });
  return response.data;
};

export const getChatHistory = async (patientId, limit = 50) => {
  const response = await api.get(`/api/chat/history/${patientId}`, {
    params: { limit },
  });
  return response.data;
};

export const clearChatHistory = async (patientId) => {
  const response = await api.delete(`/api/chat/history/${patientId}`);
  return response.data;
};

// ============================================================================
// RISK ASSESSMENT
// ============================================================================

export const getRiskSummary = async (patientId, days = 30) => {
  const response = await api.get(`/api/patient/${patientId}/risk/summary`, {
    params: { days },
  });
  return response.data;
};

// ============================================================================
// DOCUMENTS (not implemented in UI yet)
// ============================================================================

export const uploadDocument = async (patientId, file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('patient_id', patientId);
  
  const response = await api.post('/api/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Export API instance for custom requests if needed
export default api;
