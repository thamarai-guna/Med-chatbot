/**
 * AlertList Component
 * Displays high-risk patient alerts for doctors
 */

import React from 'react';
import RiskBadge from './RiskBadge';

const AlertList = ({ alerts }) => {
  const containerStyle = {
    border: '1px solid #dee2e6',
    borderRadius: '8px',
    backgroundColor: '#ffffff',
  };

  const headerStyle = {
    padding: '16px',
    borderBottom: '1px solid #dee2e6',
    fontWeight: 'bold',
    fontSize: '16px',
  };

  const alertItemStyle = {
    padding: '16px',
    borderBottom: '1px solid #dee2e6',
  };

  const emptyStyle = {
    padding: '32px',
    textAlign: 'center',
    color: '#6c757d',
  };

  if (!alerts || alerts.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={headerStyle}>Patient Alerts</div>
        <div style={emptyStyle}>
          <div>✅ No high-risk alerts</div>
          <div style={{ fontSize: '14px', marginTop: '8px' }}>
            All patients have LOW or MEDIUM risk levels
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        ⚠️ Patient Alerts ({alerts.length})
      </div>
      {alerts.map((alert, idx) => (
        <div key={idx} style={alertItemStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                {alert.patient_name || `Patient ${alert.patient_id}`}
              </div>
              <div style={{ fontSize: '14px', color: '#6c757d' }}>
                ID: {alert.patient_id}
              </div>
            </div>
            <RiskBadge level={alert.risk_level} />
          </div>
          {alert.reason && (
            <div style={{ marginTop: '8px', fontSize: '14px', color: '#495057' }}>
              {alert.reason}
            </div>
          )}
          {alert.timestamp && (
            <div style={{ marginTop: '4px', fontSize: '12px', color: '#6c757d' }}>
              {new Date(alert.timestamp).toLocaleString()}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default AlertList;
