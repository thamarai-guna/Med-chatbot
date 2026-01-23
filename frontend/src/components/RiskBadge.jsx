/**
 * RiskBadge Component
 * Displays risk level with appropriate color coding
 */

import React from 'react';

const RiskBadge = ({ level, size = 'medium' }) => {
  const getColor = (riskLevel) => {
    switch (riskLevel?.toUpperCase()) {
      case 'LOW':
        return '#28a745'; // Green
      case 'MEDIUM':
        return '#ffc107'; // Yellow
      case 'HIGH':
        return '#ff6b6b'; // Orange
      case 'CRITICAL':
        return '#dc3545'; // Red
      default:
        return '#6c757d'; // Gray
    }
  };

  const getSize = () => {
    switch (size) {
      case 'small':
        return { padding: '4px 8px', fontSize: '12px' };
      case 'large':
        return { padding: '12px 24px', fontSize: '18px' };
      default:
        return { padding: '8px 16px', fontSize: '14px' };
    }
  };

  const style = {
    backgroundColor: getColor(level),
    color: 'white',
    ...getSize(),
    borderRadius: '4px',
    fontWeight: 'bold',
    display: 'inline-block',
    textTransform: 'uppercase',
  };

  return <span style={style}>{level || 'UNKNOWN'}</span>;
};

export default RiskBadge;
