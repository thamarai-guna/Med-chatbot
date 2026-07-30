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
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);

  const { theme, isDark } = useTheme();

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  // Check report status and load documents on component mount
  useEffect(() => {
    refreshData();
  }, [patientId]);

  const refreshData = async () => {
    try {
      setLoading(true);
      await Promise.all([checkReportStatus(), loadDocuments()]);
    } catch (err) {
      console.error('Failed to refresh data:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkReportStatus = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/patient/${patientId}/report/status`
      );
      setReportStatus(response.data);
    } catch (err) {
      console.error('Failed to check report status:', err);
    }
  };

  const loadDocuments = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/documents/patient/${patientId}/list`
      );
      setDocuments(response.data.documents || []);
    } catch (err) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleDeleteDocument = async (filename) => {
    if (!window.confirm(`Are you sure you want to delete ${filename}? This will remove it from the AI's knowledge base.`)) {
      return;
    }

    try {
      setLoading(true);
      await axios.delete(
        `${API_BASE_URL}/api/documents/patient/${patientId}/${filename}`
      );

      // Refresh everything
      await refreshData();

      // Notify parent to update dashboard status
      if (onReportUploaded) {
        onReportUploaded();
      }
    } catch (err) {
      console.error('Failed to delete document:', err);
      setUploadError(`Failed to delete ${filename}`);
      setLoading(false);
    }
  };

  /**
   * Upload medical report to backend
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

      const formData = new FormData();
      formData.append('file', selectedFile);

      const response = await axios.post(
        `${API_BASE_URL}/api/patient/${patientId}/upload-report`,
        formData,
        {
          timeout: 60000, // 60 seconds for large file processing
        }
      );

      // Upload successful
      setUploadSuccess(
        `✅ Report uploaded successfully! (${response.data.chunks_count} chunks indexed)`
      );
      setSelectedFile(null);

      // Refresh report status and documents
      await refreshData();

      if (onReportUploaded) {
        onReportUploaded();
      }
    } catch (err) {
      console.error('Report upload failed:', err);
      let errorMsg = 'Upload failed';
      if (err.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      }
      setUploadError(`❌ Upload failed: ${errorMsg}`);
    } finally {
      setUploading(false);
    }
  };

  // Styles
  const containerStyle = {
    backgroundColor: 'var(--pk-bg-secondary)',
    padding: '24px',
    borderRadius: '12px',
    border: '1px solid var(--pk-border)',
    marginBottom: '24px',
    color: 'var(--pk-text)',
  };

  const statusBannerStyle = (ready) => ({
    backgroundColor: ready ? 'var(--pk-risk-low-bg)' : 'var(--pk-risk-high-bg)',
    border: `1px solid ${ready ? 'var(--pk-risk-low-border)' : 'var(--pk-risk-high-border)'}`,
    color: ready ? 'var(--pk-risk-low-text)' : 'var(--pk-risk-high-text)',
    padding: '12px 16px',
    borderRadius: '8px',
    marginBottom: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '14px',
  });

  const uploadAreaStyle = {
    border: '2px dashed var(--pk-accent)',
    borderRadius: '12px',
    padding: '24px',
    textAlign: 'center',
    backgroundColor: isDark ? 'var(--pk-bg-tertiary)' : 'var(--pk-bg-secondary)',
    cursor: 'pointer',
    transition: 'all 0.2s',
  };

  const fileItemStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px',
    backgroundColor: 'var(--pk-bg)',
    border: '1px solid var(--pk-border)',
    borderRadius: '8px',
    marginBottom: '8px',
  };

  const hasReport = reportStatus?.can_proceed_with_monitoring || false;

  return (
    <div style={containerStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h2 className="text-lg" style={{ margin: 0 }}>📋 Medical Reports</h2>
        {loading && <span className="text-sm text-muted">Refreshing...</span>}
      </div>

      {/* Status Banner */}
      <div style={statusBannerStyle(hasReport)}>
        <span style={{ fontSize: '20px' }}>{hasReport ? '✅' : '⚠️'}</span>
        <div>
          <div style={{ fontWeight: 600 }}>
            {hasReport ? 'Ready for Monitoring' : 'Action Required'}
          </div>
          <div>
            {hasReport
              ? 'Your reports are processed. You can start chatting.'
              : 'Please upload at least one medical report to enable the chatbot.'}
          </div>
        </div>
      </div>

      {/* Document List */}
      {documents.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <h3 className="text-sm text-muted" style={{ marginBottom: '12px', textTransform: 'uppercase' }}>Uploaded Files ({documents.length})</h3>
          {documents.map((doc, idx) => (
            <div key={idx} style={fileItemStyle}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '20px' }}>📄</span>
                <div>
                  <div style={{ fontWeight: 500 }}>{doc.filename}</div>
                  <div className="text-xs text-muted">
                    {Math.round(doc.size_bytes / 1024)} KB • {new Date(doc.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
              <button
                className="btn btn-outline"
                style={{ borderColor: 'var(--pk-risk-high-border)', color: 'var(--pk-risk-high-text)', padding: '4px 12px', fontSize: '12px' }}
                onClick={() => handleDeleteDocument(doc.filename)}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload Area */}
      <div>
        <h3 className="text-sm text-muted" style={{ marginBottom: '12px', textTransform: 'uppercase' }}>Upload New Report</h3>

        <div
          style={uploadAreaStyle}
          onClick={() => window.fileInput?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            if (e.dataTransfer.files[0]) setSelectedFile(e.dataTransfer.files[0]);
          }}
        >
          <input
            ref={(input) => { window.fileInput = input; }}
            type="file"
            style={{ display: 'none' }}
            onChange={(e) => setSelectedFile(e.target.files[0])}
            accept=".pdf,.jpg,.jpeg,.png,.txt"
            disabled={uploading}
          />

          <div style={{ fontSize: '32px', marginBottom: '8px' }}>📤</div>
          <div style={{ fontWeight: 500, marginBottom: '4px' }}>
            {selectedFile ? selectedFile.name : 'Click or Drag to Upload'}
          </div>
          <div className="text-xs text-muted">PDF, JPG, PNG, TXT (Max 10MB)</div>
        </div>

        {selectedFile && (
          <div style={{ marginTop: '12px', display: 'flex', gap: '12px' }}>
            <button
              className="btn btn-primary"
              onClick={handleUploadReport}
              disabled={uploading}
              style={{ flex: 1 }}
            >
              {uploading ? 'Uploading...' : 'Confirm Upload'}
            </button>
            <button
              className="btn btn-outline"
              onClick={() => setSelectedFile(null)}
              disabled={uploading}
            >
              Cancel
            </button>
          </div>
        )}

        {/* Feedback Messages */}
        {uploadError && (
          <div style={{ marginTop: '12px', color: 'var(--pk-risk-high-text)', fontSize: '14px' }}>
            {uploadError}
          </div>
        )}
        {uploadSuccess && (
          <div style={{ marginTop: '12px', color: 'var(--pk-risk-low-text)', fontSize: '14px' }}>
            {uploadSuccess}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportUploadComponent;
