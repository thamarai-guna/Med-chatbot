/**
 * AlertList Component
 * Displays high-risk patient alerts for doctors
 */

import React from 'react';
import { useTheme } from '../context/ThemeContext';
import RiskBadge from './RiskBadge';

const AlertList = ({ alerts }) => {
  const { theme } = useTheme();

  const containerStyle = {
    backgroundColor: theme.bgSecondary,
    borderRadius: '12px',
    border: `1px solid ${theme.border}`,
    boxShadow: `0 2px 8px ${theme.shadow}`,
    transition: 'all 0.3s',
  };

  const headerStyle = {
    padding: '16px 20px',
    borderBottom: `1px solid ${theme.border}`,
    fontWeight: '600',
    fontSize: '15px',
    color: theme.text,
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'all 0.3s',
  };

  const alertItemStyle = (riskLevel) => {
    const borderColorMap = {
      LOW: theme.riskLow.border,
      MEDIUM: theme.riskMedium.border,
      HIGH: theme.riskHigh.border,
      CRITICAL: theme.riskCritical.border,
    };

    return {
      padding: '16px 20px',
      borderBottom: `1px solid ${theme.border}`,
      borderLeft: `4px solid ${borderColorMap[riskLevel] || theme.border}`,
      transition: 'background-color 0.2s',
      backgroundColor: 'transparent',
    };
  };

  const emptyStyle = {
    padding: '40px 20px',
    textAlign: 'center',
    color: theme.textSecondary,
    transition: 'color 0.3s',
  };

  const emptyIconStyle = {
    fontSize: '36px',
    marginBottom: '12px',
  };

  const emptyTitleStyle = {
    fontWeight: '600',
    fontSize: '15px',
    color: theme.text,
    marginBottom: '4px',
    transition: 'color 0.3s',
  };

  const alertNameStyle = {
    fontWeight: '600',
    fontSize: '14px',
    color: theme.text,
    marginBottom: '4px',
    transition: 'color 0.3s',
  };

  const alertIdStyle = {
    fontSize: '13px',
    color: theme.textSecondary,
    transition: 'color 0.3s',
  };

  const alertReasonStyle = {
    marginTop: '8px',
    fontSize: '13px',
    color: theme.textSecondary,
    lineHeight: '1.4',
    transition: 'color 0.3s',
  };

  const alertTimeStyle = {
    marginTop: '6px',
    fontSize: '12px',
    color: theme.textTertiary,
    transition: 'color 0.3s',
  };

  const alertHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '4px',
    gap: '12px',
  };

  if (!alerts || alerts.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={headerStyle}>
          <span>🔔</span>
          Patient Alerts
        </div>
        <div style={emptyStyle}>
          <div style={emptyIconStyle}>✅</div>
          <div style={emptyTitleStyle}>No high-risk alerts</div>
          <div style={{ fontSize: '13px', color: theme.textSecondary }}>
            All patients have LOW or MEDIUM risk levels
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <span>🔔</span>
        Alerts ({alerts.length})
      </div>
      {alerts.map((alert, idx) => (
        <div key={idx} style={alertItemStyle(alert.risk_level)}>
          <div style={alertHeaderStyle}>
            <div style={{ flex: 1 }}>
              <div style={alertNameStyle}>
                {alert.patient_name || `Patient ${alert.patient_id}`}
              </div>
              <div style={alertIdStyle}>
                ID: {alert.patient_id}
              </div>
            </div>
            <RiskBadge level={alert.risk_level} size="small" />
          </div>
          {alert.reason && (
            <div style={alertReasonStyle}>
              {alert.reason}
            </div>
          )}
          {alert.timestamp && (
            <div style={alertTimeStyle}>
              {new Date(alert.timestamp).toLocaleString()}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default AlertList;
