/**
 * RiskBadge Component
 * Displays risk level with color coding and modern styling
 */

import React from 'react';
import { useTheme } from '../context/ThemeContext';

const RiskBadge = ({ level, size = 'medium' }) => {
  const { theme } = useTheme();

  const getColorScheme = (riskLevel) => {
    switch (riskLevel?.toUpperCase()) {
      case 'LOW':
        return theme.riskLow;
      case 'MEDIUM':
        return theme.riskMedium;
      case 'HIGH':
        return theme.riskHigh;
      case 'CRITICAL':
        return theme.riskCritical;
      default:
        return {
          bg: theme.bgTertiary,
          border: theme.border,
          text: theme.textSecondary,
        };
    }
  };

  const getSizeConfig = () => {
    switch (size) {
      case 'small':
        return { padding: '4px 10px', fontSize: '12px', letterSpacing: '0.5px' };
      case 'large':
        return { padding: '10px 20px', fontSize: '16px', letterSpacing: '1px' };
      default:
        return { padding: '6px 14px', fontSize: '13px', letterSpacing: '0.5px' };
    }
  };

  const colorScheme = getColorScheme(level);
  const sizeConfig = getSizeConfig();

  const style = {
    backgroundColor: colorScheme.bg,
    color: colorScheme.text,
    border: `1.5px solid ${colorScheme.border}`,
    ...sizeConfig,
    borderRadius: '6px',
    fontWeight: '600',
    display: 'inline-block',
    textTransform: 'uppercase',
    transition: 'all 0.3s',
  };

  return <span style={style}>{level || 'UNKNOWN'}</span>;
};

export default RiskBadge;
