/**
 * Medical Report Upload Component
 * 
 * MANDATORY: Patients must upload medical reports BEFORE chatting
 * This component handles:
 * 1. Report status checking
 * 2. File upload (PDF, Image, Text)
 * 3. Processing feedback
 * 4. Blocking message if no report exists
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useTheme } from '../context/ThemeContext';

const ReportUploadComponent = ({ patientId, onReportUploaded }) => {
  const [reportStatus, setReportStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const { theme, isDark } = useTheme();

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // Check report status on component mount
  useEffect(() => {
    checkReportStatus();
  }, [patientId]);

  /**
   * Check if patient has uploaded medical reports
   * CRITICAL: This determines if chatbot is enabled
   */
  const checkReportStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${API_BASE_URL}/api/patient/${patientId}/report/status`
      );
      setReportStatus(response.data);
    } catch (err) {
      console.error('Failed to check report status:', err);
      setUploadError('Failed to check report status. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Upload medical report to backend
   * Supported formats: PDF, Images (JPG/PNG), Plain Text
   */
  const handleUploadReport = async () => {
    if (!selectedFile) {
      setUploadError('Please select a file to upload');
      return;
    }

    // Validate file type
    const validTypes = [
      'application/pdf',
      'image/jpeg',
      'image/png',
      'image/jpg',
      'text/plain',
    ];
    
    if (!validTypes.includes(selectedFile.type)) {
      setUploadError(
        'Invalid file type. Please upload PDF, Image (JPG/PNG), or Text file.'
      );
      return;
    }

    // Validate file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setUploadError('File is too large. Maximum size is 10MB.');
      return;
    }

    try {
      setUploading(true);
      setUploadError(null);
      setUploadSuccess(null);

      // Debug: Log patientId
      console.log('Uploading report for patient:', patientId);
      console.log('File:', selectedFile?.name, 'Size:', selectedFile?.size);

      const formData = new FormData();
      formData.append('file', selectedFile);

      // NOTE: Do NOT set Content-Type header - let axios/browser handle it
      // Setting it manually breaks the multipart boundary
      const response = await axios.post(
        `${API_BASE_URL}/api/patient/${patientId}/upload-report`,
        formData,
        {
          timeout: 60000, // 60 seconds for large file processing
        }
      );

      console.log('Upload response:', response.data);

      // Upload successful
      setUploadSuccess(
        `✅ Report uploaded successfully! (${response.data.chunks_count} chunks indexed)`
      );
      setSelectedFile(null);
      
      // Refresh report status
      setTimeout(() => {
        checkReportStatus();
        if (onReportUploaded) {
          onReportUploaded();
        }
      }, 1000);
    } catch (err) {
      console.error('Report upload failed:', err);
      console.error('Error response:', err.response?.data);
      console.error('Error status:', err.response?.status);
      
      let errorMsg = 'Upload failed';
      if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      } else if (err.response?.status === 400) {
        errorMsg = 'Bad request - file may be invalid or too large';
      } else if (err.response?.status === 404) {
        errorMsg = 'Patient not found';
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      setUploadError(`❌ Upload failed: ${errorMsg}`);
    } finally {
      setUploading(false);
    }
  };

  const containerStyle = {
    backgroundColor: theme.bgSecondary,
    padding: '24px',
    borderRadius: '12px',
    border: `1px solid ${theme.border}`,
    boxShadow: `0 2px 8px ${theme.shadow}`,
    marginBottom: '24px',
    transition: 'all 0.3s',
    color: theme.text,
  };

  const warningStyle = {
    backgroundColor: theme.riskHigh.bg,
    border: `1px solid ${theme.riskHigh.border}`,
    color: theme.riskHigh.text,
    padding: '12px 16px',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '14px',
    transition: 'all 0.3s',
  };

  const successStyle = {
    backgroundColor: theme.riskLow.bg,
    border: `1px solid ${theme.riskLow.border}`,
    color: theme.riskLow.text,
    padding: '12px 16px',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '14px',
    transition: 'all 0.3s',
  };

  const errorStyle = {
    backgroundColor: theme.riskHigh.bg,
    border: `1px solid ${theme.riskHigh.border}`,
    color: theme.riskHigh.text,
    padding: '12px 16px',
    borderRadius: '8px',
    marginBottom: '16px',
    fontSize: '14px',
    transition: 'all 0.3s',
  };

  const uploadAreaStyle = {
    border: `2px dashed ${theme.accent}`,
    borderRadius: '12px',
    padding: '32px',
    textAlign: 'center',
    backgroundColor: isDark ? theme.bgTertiary : theme.bgSecondary,
    marginBottom: '16px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    color: theme.text,
  };

  const fileInputStyle = {
    display: 'none',
  };

  const buttonStyle = {
    padding: '10px 20px',
    backgroundColor: theme.accent,
    color: '#ffffff',
    border: 'none',
    borderRadius: '8px',
    cursor: uploading ? 'not-allowed' : 'pointer',
    fontWeight: '600',
    opacity: uploading ? 0.7 : 1,
    boxShadow: `0 1px 2px ${theme.shadow}`,
    transition: 'all 0.2s ease',
  };

  const statusBadgeStyle = (hasReport) => ({
    display: 'inline-block',
    padding: '8px 16px',
    borderRadius: '20px',
    fontWeight: '600',
    fontSize: '14px',
    backgroundColor: hasReport ? theme.riskLow.bg : theme.riskHigh.bg,
    color: hasReport ? theme.riskLow.text : theme.riskHigh.text,
    border: `1px solid ${hasReport ? theme.riskLow.border : theme.riskHigh.border}`,
  });

  // Loading state
  if (loading) {
    return (
      <div style={containerStyle}>
        <h2 style={{ marginTop: 0 }}>📋 Medical Report Upload</h2>
        <div style={{ textAlign: 'center', padding: '20px' }}>
          Loading report status...
        </div>
      </div>
    );
  }

  const hasReport = reportStatus?.has_medical_report || false;

  return (
    <div style={containerStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 style={{ margin: 0, color: theme.text }}>📋 Medical Report Upload</h2>
        <span style={statusBadgeStyle(hasReport)}>
          {hasReport ? '✅ Report Uploaded' : '⚠️ No Report'}
        </span>
      </div>

      {/* Status Message */}
      {hasReport ? (
        <div style={successStyle}>
          <strong>✅ Status: Ready for Monitoring</strong><br/>
          Your medical report has been uploaded and indexed. You can now use the chatbot and symptom monitoring features.
        </div>
      ) : (
        <div style={warningStyle}>
          <strong>⚠️ MANDATORY: Medical Report Required</strong><br/>
          Your medical reports must be uploaded BEFORE you can use the chatbot or symptom monitoring. 
          This ensures all AI responses are personalized to your medical history.
        </div>
      )}

      {/* Upload Section (only if no report yet) */}
      {!hasReport && (
        <>
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ marginBottom: '12px', color: theme.text }}>Upload Your Medical Report</h3>
            <p style={{ color: theme.textSecondary, fontSize: '14px' }}>
              <strong>Supported formats:</strong> PDF, Images (JPG/PNG), or Plain Text<br/>
              <strong>Max size:</strong> 10MB<br/>
              <strong>Examples:</strong> Discharge summary, medical history, test results, doctor's notes
            </p>
          </div>

          {/* File Input Area */}
          <div
            style={uploadAreaStyle}
            onDragOver={(e) => {
              e.preventDefault();
              e.currentTarget.style.backgroundColor = isDark ? theme.bgSecondary : theme.bgTertiary;
            }}
            onDragLeave={(e) => {
              e.currentTarget.style.backgroundColor = '#f0f7ff';
            }}
            onDrop={(e) => {
              e.preventDefault();
              e.currentTarget.style.backgroundColor = isDark ? theme.bgTertiary : theme.bgSecondary;
              if (e.dataTransfer.files[0]) {
                setSelectedFile(e.dataTransfer.files[0]);
              }
            }}
          >
            <input
              ref={(input) => {
                window.fileInput = input;
              }}
              type="file"
              style={fileInputStyle}
              onChange={(e) => setSelectedFile(e.target.files[0])}
              accept=".pdf,.jpg,.jpeg,.png,.txt"
              disabled={uploading}
            />
            <div style={{ fontSize: '48px', marginBottom: '12px' }}>📁</div>
            <div style={{ fontSize: '16px', fontWeight: 600, marginBottom: '8px', color: theme.text }}>
              {selectedFile ? selectedFile.name : 'Drag and drop your file here'}
            </div>
            <div style={{ fontSize: '14px', color: theme.textSecondary, marginBottom: '16px' }}>
              or
            </div>
            <button
              onClick={() => window.fileInput?.click()}
              style={{
                padding: '8px 16px',
                backgroundColor: theme.bgSecondary,
                border: `1px solid ${theme.accent}`,
                color: theme.accent,
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 600,
                boxShadow: `0 1px 2px ${theme.shadow}`,
              }}
              disabled={uploading}
            >
              Browse Files
            </button>
          </div>

          {/* Error Message */}
          {uploadError && (
            <div style={errorStyle}>
              {uploadError}
            </div>
          )}

          {/* Success Message */}
          {uploadSuccess && (
            <div style={successStyle}>
              {uploadSuccess}
            </div>
          )}

          {/* Upload Button */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={handleUploadReport}
              style={buttonStyle}
              disabled={!selectedFile || uploading}
            >
              {uploading ? 'Uploading...' : '📤 Upload Report'}
            </button>
            {selectedFile && (
              <button
                onClick={() => setSelectedFile(null)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: theme.bgTertiary,
                  color: theme.text,
                  border: `1px solid ${theme.border}`,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: 600,
                }}
                disabled={uploading}
              >
                Clear
              </button>
            )}
          </div>
        </>
      )}

      {/* Info Section */}
      <div style={{
        marginTop: '24px',
        padding: '16px',
        backgroundColor: theme.bgSecondary,
        borderRadius: '8px',
        border: `1px solid ${theme.border}`,
        fontSize: '13px',
        color: theme.textSecondary,
        lineHeight: '1.6',
        transition: 'all 0.3s',
      }}>
        <strong style={{ color: theme.text }}>ℹ️ How it works:</strong>
        <ul style={{ margin: '8px 0 0 20px', paddingLeft: 0 }}>
          <li>Your report is securely processed and stored</li>
          <li>Text is extracted and split into indexed chunks</li>
          <li>Your medical history personalizes all AI responses</li>
          <li>The chatbot uses both your report and medical guidelines</li>
          <li>Your data is private and not shared with other patients</li>
        </ul>
      </div>
    </div>
  );
};

export default ReportUploadComponent;
