import React, { useState, useEffect } from 'react';
import { getAlerts, acknowledgeAlert } from '../../services/api';
import './AlertsPanel.css';

const AlertsPanel = ({ userRole }) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('NEW'); // NEW, ACKNOWLEDGED, ALL
  const [error, setError] = useState(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const statusFilter = filter === 'ALL' ? null : filter;
      const response = await getAlerts(statusFilter);
      setAlerts(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch alerts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    // Poll every 5 seconds for new alerts
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, [filter]);

  const handleAcknowledge = async (alertId) => {
    try {
      await acknowledgeAlert(alertId);
      // Refresh alerts
      fetchAlerts();
    } catch (err) {
      alert('Failed to acknowledge alert: ' + err.response?.data?.detail);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'HIGH':
        return 'severity-high';
      case 'MEDIUM':
        return 'severity-medium';
      case 'LOW':
        return 'severity-low';
      default:
        return '';
    }
  };

  const getAlertTypeLabel = (type) => {
    switch (type) {
      case 'VITALS_ABNORMAL':
        return '🩺 Vitals Abnormal';
      case 'COMA_MOVEMENT_DETECTED':
        return '👁️ Movement Detected';
      case 'HIGH_RISK_FROM_CHATBOT':
        return '🤖 High Risk Alert';
      default:
        return type;
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000 / 60); // minutes

    if (diff < 1) return 'Just now';
    if (diff < 60) return `${diff}m ago`;
    if (diff < 1440) return `${Math.floor(diff / 60)}h ago`;
    return date.toLocaleString();
  };

  if (loading && alerts.length === 0) {
    return <div className="alerts-loading">Loading alerts...</div>;
  }

  return (
    <div className="alerts-panel">
      <div className="alerts-header">
        <h2>🚨 Alerts Dashboard</h2>
        <div className="alerts-filters">
          <button
            className={filter === 'NEW' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('NEW')}
          >
            New ({alerts.filter(a => a.status === 'NEW').length})
          </button>
          <button
            className={filter === 'ACKNOWLEDGED' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('ACKNOWLEDGED')}
          >
            Acknowledged
          </button>
          <button
            className={filter === 'ALL' ? 'filter-btn active' : 'filter-btn'}
            onClick={() => setFilter('ALL')}
          >
            All
          </button>
        </div>
      </div>

      {error && <div className="alerts-error">{error}</div>}

      <div className="alerts-list">
        {alerts.length === 0 ? (
          <div className="no-alerts">
            <p>✅ No alerts at the moment</p>
          </div>
        ) : (
          alerts.map((alert) => (
            <div
              key={alert.id}
              className={`alert-card ${getSeverityColor(alert.severity)} ${
                alert.status === 'NEW' ? 'alert-new' : 'alert-acknowledged'
              }`}
            >
              <div className="alert-header-row">
                <span className="alert-type">{getAlertTypeLabel(alert.alert_type)}</span>
                <span className={`alert-severity ${getSeverityColor(alert.severity)}`}>
                  {alert.severity}
                </span>
              </div>

              <div className="alert-patient">
                <strong>{alert.patient_name}</strong>
                <span className="patient-number">#{alert.patient_number}</span>
              </div>

              <div className="alert-message">{alert.message}</div>

              <div className="alert-meta">
                <span className="alert-source">Source: {alert.source}</span>
                <span className="alert-time">{formatTimestamp(alert.created_at)}</span>
              </div>

              {alert.status === 'NEW' ? (
                <button
                  className="btn-acknowledge"
                  onClick={() => handleAcknowledge(alert.id)}
                >
                  ✓ Acknowledge
                </button>
              ) : (
                <div className="alert-acknowledged-info">
                  ✓ Acknowledged by {alert.acknowledged_by_name} at{' '}
                  {new Date(alert.acknowledged_at).toLocaleString()}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsPanel;
