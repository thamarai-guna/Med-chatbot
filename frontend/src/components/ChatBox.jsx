/**
 * ChatBox Component
 * Main chat interface with input and message history
 */

import React, { useState, useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import { sendChatMessage, getChatHistory } from '../api/api';

const ChatBox = ({ patientId }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Load chat history on mount
  useEffect(() => {
    if (patientId) {
      loadHistory();
    }
  }, [patientId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
    height: '600px',
    border: '1px solid #dee2e6',
    borderRadius: '8px',
    overflow: 'hidden',
  };

  const messagesStyle = {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    backgroundColor: '#ffffff',
    display: 'flex',
    flexDirection: 'column',
  };

  const inputContainerStyle = {
    padding: '16px',
    backgroundColor: '#f8f9fa',
    borderTop: '1px solid #dee2e6',
    display: 'flex',
    gap: '8px',
  };

  const inputStyle = {
    flex: 1,
    padding: '12px',
    border: '1px solid #ced4da',
    borderRadius: '4px',
    fontSize: '14px',
  };

  const buttonStyle = {
    padding: '12px 24px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: loading ? 'not-allowed' : 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
    opacity: loading ? 0.6 : 1,
  };

  return (
    <div style={containerStyle}>
      <div style={messagesStyle}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#6c757d', marginTop: '20px' }}>
            Start a conversation by typing a message below...
          </div>
        )}
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} isUser={msg.isUser} />
        ))}
        {loading && (
          <div style={{ textAlign: 'center', color: '#6c757d' }}>
            AI is thinking...
          </div>
        )}
        {error && (
          <div style={{ color: '#dc3545', padding: '12px', backgroundColor: '#f8d7da', borderRadius: '4px', marginTop: '8px' }}>
            Error: {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div style={inputContainerStyle}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your medical question..."
          style={inputStyle}
          disabled={loading}
        />
        <button onClick={handleSend} disabled={loading} style={buttonStyle}>
          {loading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
