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
  const [showJumpToLatest, setShowJumpToLatest] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const { theme } = useTheme();

  const suggestedPrompts = [
    'What are common side effects of my medication?',
    'I have a fever and cough—what should I do?',
    'Explain my latest lab results in simple terms.',
    'How should I manage my diabetes today?',
  ];

  useEffect(() => {
    if (patientId) {
      loadHistory();
    }
  }, [patientId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleScroll = () => {
    const el = messagesContainerRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40;
    setShowJumpToLatest(!nearBottom);
  };

  const loadHistory = async () => {
    try {
      const history = await getChatHistory(patientId);
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

    const newUserMsg = {
      message: userMessage,
      isUser: true,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, newUserMsg]);
    setLoading(true);

    try {
      const response = await sendChatMessage(patientId, userMessage);
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
    height: '100%', // Changed from fixed 650px to 100%
    backgroundColor: 'var(--pk-bg-secondary)',
    overflow: 'hidden',
  };

  const messagesStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '24px',
    backgroundColor: 'var(--pk-bg-secondary)',
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    transition: 'background-color 0.3s',
  };

  const inputContainerStyle = {
    padding: '16px 24px 24px 24px',
    backgroundColor: 'var(--pk-bg-secondary)',
    borderTop: '1px solid var(--pk-border)',
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
    border: '1px solid var(--pk-border)',
    borderRadius: '24px',
    fontSize: '15px',
    backgroundColor: 'var(--pk-bg)',
    color: 'var(--pk-text)',
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

  const chipStyle = {
    display: 'inline-block',
    padding: '8px 12px',
    marginRight: '8px',
    marginTop: '8px',
    borderRadius: '16px',
    border: `1px solid ${theme.border}`,
    backgroundColor: theme.bg,
    color: theme.text,
    fontSize: '13px',
    cursor: 'pointer',
    boxShadow: `0 1px 2px ${theme.shadow}`,
  };

  const jumpButtonStyle = {
    position: 'sticky',
    bottom: 12,
    alignSelf: 'center',
    padding: '6px 10px',
    backgroundColor: theme.bgTertiary,
    color: theme.text,
    border: `1px solid ${theme.border}`,
    borderRadius: '12px',
    fontSize: '12px',
    cursor: 'pointer',
    boxShadow: `0 1px 2px ${theme.shadow}`,
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
      <div style={messagesStyle} onScroll={handleScroll} ref={messagesContainerRef}>
        {messages.length === 0 && (
          <div style={emptyStateStyle}>
            <div style={{ fontSize: '18px', fontWeight: '500', marginBottom: '8px' }}>
              👋 Welcome to Your Medical Assistant
            </div>
            <div>Type your medical question to get started</div>
            <div style={{ marginTop: '12px' }}>
              {suggestedPrompts.map((p, i) => (
                <span key={i} style={chipStyle} onClick={() => setInputMessage(p)}>
                  {p}
                </span>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} isUser={msg.isUser} />
        ))}

        {loading && (
          <div style={loadingStyle}>
            <span style={{ display: 'inline-block', width: 6, height: 6, borderRadius: 6, backgroundColor: theme.accent, marginRight: 4, opacity: 0.9 }}></span>
            <span style={{ display: 'inline-block', width: 6, height: 6, borderRadius: 6, backgroundColor: theme.accent, marginRight: 4, opacity: 0.7 }}></span>
            <span style={{ display: 'inline-block', width: 6, height: 6, borderRadius: 6, backgroundColor: theme.accent, opacity: 0.5 }}></span>
          </div>
        )}

        {error && (
          <div style={errorStyle}>
            ⚠️ {error}
          </div>
        )}

        {showJumpToLatest && (
          <button style={jumpButtonStyle} onClick={scrollToBottom}>Jump to latest ↓</button>
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
        <button onClick={handleSend} disabled={loading} style={buttonStyle} aria-label="Send message">
          {loading ? '⏳' : '➤'}
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
