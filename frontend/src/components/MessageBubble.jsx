/**
 * MessageBubble Component
 * Displays individual chat messages with modern styling
 */

import React from 'react';
import { useTheme } from '../context/ThemeContext';
import RiskBadge from './RiskBadge';

const MessageBubble = ({ message, isUser }) => {
  const { theme } = useTheme();

  const bubbleStyle = {
    padding: '12px 16px',
    marginBottom: '8px',
    borderRadius: '12px',
    maxWidth: '70%',
    wordWrap: 'break-word',
    lineHeight: '1.5',
    animation: 'fadeInMessage 0.3s ease-in-out',
    backgroundColor: isUser ? theme.bubbleUser : theme.bubbleBot,
    color: isUser ? 'white' : theme.bubbleText,
    boxShadow: isUser ? `0 2px 8px ${theme.shadow}` : `0 1px 3px ${theme.shadow}`,
    transition: 'all 0.3s',
  };

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: isUser ? 'flex-end' : 'flex-start',
    marginBottom: '12px',
  };

  const textStyle = {
    fontSize: '15px',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  };

  const riskSectionStyle = {
    marginTop: '10px',
    paddingTop: '8px',
    borderTop: `1px solid ${isUser ? 'rgba(255,255,255,0.2)' : theme.border}`,
    transition: 'border-color 0.3s',
  };

  const riskReasonStyle = {
    fontSize: '13px',
    marginTop: '6px',
    opacity: isUser ? 0.95 : 0.8,
  };

  return (
    <div style={containerStyle}>
      <div style={bubbleStyle}>
        <div style={textStyle}>
          {message.message || message.question || message.answer}
        </div>
        {message.risk_level && (
          <div style={riskSectionStyle}>
            <RiskBadge level={message.risk_level} size="small" />
            {message.risk_reason && (
              <div style={riskReasonStyle}>
                {message.risk_reason}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
