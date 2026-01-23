import React from 'react';
import { useTheme } from '../context/ThemeContext';

const ThemeToggle = () => {
  const { isDark, toggleTheme, theme } = useTheme();

  const toggleContainerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    cursor: 'pointer',
    padding: '4px 8px',
    borderRadius: '20px',
    backgroundColor: theme.bgSecondary,
    border: `1px solid ${theme.border}`,
    transition: 'all 0.2s',
  };

  const toggleTrackStyle = {
    width: '44px',
    height: '24px',
    backgroundColor: isDark ? theme.accent : '#cbd5e1',
    borderRadius: '12px',
    position: 'relative',
    transition: 'background-color 0.3s',
    display: 'flex',
    alignItems: 'center',
    padding: '2px',
  };

  const toggleThumbStyle = {
    width: '20px',
    height: '20px',
    backgroundColor: 'white',
    borderRadius: '10px',
    position: 'absolute',
    left: isDark ? '22px' : '2px',
    transition: 'left 0.3s',
    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
  };

  const iconStyle = {
    fontSize: '16px',
    display: 'flex',
    alignItems: 'center',
    transition: 'opacity 0.2s',
    opacity: isDark ? 0.3 : 1,
  };

  const darkIconStyle = {
    ...iconStyle,
    opacity: isDark ? 1 : 0.3,
  };

  return (
    <div style={toggleContainerStyle} onClick={toggleTheme} title={`Switch to ${isDark ? 'light' : 'dark'} mode`}>
      <span style={iconStyle}>☀️</span>
      <div style={toggleTrackStyle}>
        <div style={toggleThumbStyle}></div>
      </div>
      <span style={darkIconStyle}>🌙</span>
    </div>
  );
};

export default ThemeToggle;
