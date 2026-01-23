/**
 * MessageBubble Component
 * Displays individual chat messages
 */

import React from 'react';
import RiskBadge from './RiskBadge';

const MessageBubble = ({ message, isUser }) => {
  const bubbleStyle = {
    padding: '12px 16px',
    marginBottom: '12px',
    borderRadius: '8px',
    maxWidth: '80%',
    alignSelf: isUser ? 'flex-end' : 'flex-start',
    backgroundColor: isUser ? '#007bff' : '#f1f3f5',
    color: isUser ? 'white' : '#212529',
    wordWrap: 'break-word',
  };

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: isUser ? 'flex-end' : 'flex-start',
    marginBottom: '16px',
  };

  const metaStyle = {
    fontSize: '12px',
    color: '#6c757d',
    marginTop: '4px',
  };

  return (
    <div style={containerStyle}>
      <div style={bubbleStyle}>
        <div>{message.message || message.question || message.answer}</div>
        {message.risk_level && (
          <div style={{ marginTop: '8px' }}>
            <RiskBadge level={message.risk_level} size="small" />
            {message.risk_reason && (
              <div style={{ fontSize: '12px', marginTop: '4px', opacity: 0.9 }}>
                {message.risk_reason}
              </div>
            )}
          </div>
        )}
        {message.source_documents && message.source_documents.length > 0 && (
          <details style={{ marginTop: '8px', fontSize: '12px' }}>
            <summary style={{ cursor: 'pointer' }}>Sources ({message.source_documents.length})</summary>
            <div style={{ marginTop: '4px', opacity: 0.8 }}>
              {message.source_documents.slice(0, 2).map((doc, idx) => (
                <div key={idx} style={{ marginTop: '4px' }}>
                  {doc.substring(0, 100)}...
                </div>
              ))}
            </div>
          </details>
        )}
      </div>
      {message.timestamp && (
        <div style={metaStyle}>
          {new Date(message.timestamp).toLocaleString()}
        </div>
      )}
    </div>
  );
};

export default MessageBubble;
