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

export const sendChatMessage = async (patientId, message) => {
  const response = await api.post('/api/chat/query', {
    patient_id: patientId,
    message: message,
    // No vector_store_name - uses dual retrieval automatically
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
// PATIENT-SPECIFIC DOCUMENT MANAGEMENT
// ============================================================================

export const uploadPatientDocuments = async (patientId, files, uploaderRole = 'patient') => {
  const formData = new FormData();
  
  // Append multiple files
  files.forEach(file => {
    formData.append('files', file);
  });
  
  const response = await api.post(`/api/documents/patient/${patientId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    params: {
      uploader_role: uploaderRole,
    },
  });
  return response.data;
};

export const listPatientDocuments = async (patientId) => {
  const response = await api.get(`/api/documents/patient/${patientId}/list`);
  return response.data;
};

export const deletePatientDocument = async (patientId, filename) => {
  const response = await api.delete(`/api/documents/patient/${patientId}/${filename}`);
  return response.data;
};

// ============================================================================
// DAILY QUESTIONS
// ============================================================================

export const generateDailyQuestion = async (patientId) => {
  const response = await api.post(`/api/questions/daily/${patientId}`);
  return response.data;
};

export const saveDailyAnswer = async (patientId, question, answer, metadata = null) => {
  const response = await api.post(`/api/questions/daily/${patientId}/answer`, {
    question: question,
    answer: answer,
    question_metadata: metadata,
  });
  return response.data;
};

export const getDailyAnswersHistory = async (patientId, days = 7) => {
  const response = await api.get(`/api/questions/daily/${patientId}/history`, {
    params: { days },
  });
  return response.data;
};

// ============================================================================
// DEPRECATED (OLD DOCUMENT UPLOAD - REMOVE)
// ============================================================================

export const uploadDocument = async (patientId, file) => {
  console.warn('uploadDocument() is deprecated. Use uploadPatientDocuments() instead.');
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
