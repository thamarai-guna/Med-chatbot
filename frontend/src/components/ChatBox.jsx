/**
 * ChatBox Component
 * Main chat interface with ChatGPT-style layout
 */

import React, { useState, useEffect, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';
import MessageBubble from './MessageBubble';
import { sendChatMessage, getChatHistory } from '../api/api';

const ChatBox = ({ patientId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const { theme } = useTheme();

  // Load chat history on mount
  useEffect(() => {
    if (patientId) {
      loadHistory();
    }
  }, [patientId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadHistory = async () => {
    try {
      const history = await getChatHistory(patientId);
      // Convert history format to messages
      const formattedMessages = [];
      history.history?.forEach((item) => {
        formattedMessages.push({
          message: item.question,
          isUser: true,
          timestamp: item.timestamp,
        });
        formattedMessages.push({
          message: item.answer,
          isUser: false,
          risk_level: item.risk_level,
          risk_reason: item.risk_reason,
          source_documents: item.source_documents,
          timestamp: item.timestamp,
        });
      });
      setMessages(formattedMessages);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  const handleSend = async () => {
    if (!inputMessage.trim() || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setError(null);

    // Add user message to UI immediately
    const newUserMsg = {
      message: userMessage,
      isUser: true,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMsg]);

    setLoading(true);

    try {
      const response = await sendChatMessage(patientId, userMessage);

      // Add AI response to messages
      const aiMessage = {
        message: response.answer,
        isUser: false,
        risk_level: response.risk_level,
        risk_reason: response.risk_reason,
        source_documents: response.source_documents,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (err) {
      setError(err.message || 'Failed to send message');
      // Remove user message on error
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const containerStyle = {
    display: 'flex',
    flexDirection: 'column',
    height: '650px',
    backgroundColor: theme.bgSecondary,
    borderRadius: '12px',
    border: `1px solid ${theme.border}`,
    overflow: 'hidden',
    boxShadow: `0 4px 12px ${theme.shadowMd}`,
    transition: 'all 0.3s',
  };

  const messagesStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    backgroundColor: theme.bgSecondary,
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    transition: 'background-color 0.3s',
  };

  const inputContainerStyle = {
    padding: '16px 24px 24px 24px',
    backgroundColor: theme.bgSecondary,
    borderTop: `1px solid ${theme.border}`,
    display: 'flex',
    gap: '12px',
    alignItems: 'flex-end',
    transition: 'all 0.3s',
  };

  const inputWrapperStyle = {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
  };

  const inputStyle = {
    width: '100%',
    padding: '12px 16px',
    border: `1px solid ${theme.border}`,
    borderRadius: '24px',
    fontSize: '15px',
    backgroundColor: theme.bg,
    color: theme.text,
    outline: 'none',
    transition: 'all 0.2s',
  };

  const buttonStyle = {
    padding: '10px 16px',
    backgroundColor: loading ? theme.borderLight : theme.accent,
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: loading ? 'not-allowed' : 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    opacity: loading ? 0.7 : 1,
    transition: 'background-color 0.2s',
  };

  const emptyStateStyle = {
    textAlign: 'center',
    color: theme.textTertiary,
    marginTop: '40px',
    fontSize: '15px',
    transition: 'color 0.3s',
  };

  const loadingStyle = {
    textAlign: 'center',
    color: theme.accent,
    fontSize: '14px',
    fontWeight: '500',
    marginBottom: '8px',
    transition: 'color 0.3s',
  };

  const errorStyle = {
    color: theme.riskCritical.text,
    padding: '12px 16px',
    backgroundColor: theme.riskCritical.bg,
    borderRadius: '8px',
    marginTop: '12px',
    fontSize: '14px',
    border: `1px solid ${theme.riskCritical.border}`,
    transition: 'all 0.3s',
  };

  return (
    <div style={containerStyle}>
      <div style={messagesStyle}>
        {messages.length === 0 && (
          <div style={emptyStateStyle}>
            <div style={{ fontSize: '18px', fontWeight: '500', marginBottom: '8px' }}>
              👋 Welcome to Your Medical Assistant
            </div>
            <div>Type your medical question to get started</div>
          </div>
        )}
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} isUser={msg.isUser} />
        ))}
        {loading && (
          <div style={loadingStyle}>
            ✓ AI is thinking...
          </div>
        )}
        {error && (
          <div style={errorStyle}>
            ⚠️ {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div style={inputContainerStyle}>
        <div style={inputWrapperStyle}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your response here…"
            style={inputStyle}
            disabled={loading}
          />
        </div>
        <button onClick={handleSend} disabled={loading} style={buttonStyle}>
          {loading ? '⏳' : '→'}
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
