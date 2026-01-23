import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(() => {
    // Check localStorage for saved preference
    const saved = localStorage.getItem('theme-preference');
    if (saved) {
      return saved === 'dark';
    }
    // Check system preference
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    // Save preference to localStorage
    localStorage.setItem('theme-preference', isDark ? 'dark' : 'light');
    // Update document data attribute for CSS
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const toggleTheme = () => setIsDark(!isDark);

  // Theme colors
  const colors = {
    light: {
      // Background
      bg: '#ffffff',
      bgSecondary: '#f9fafb',
      bgTertiary: '#f3f4f6',
      
      // Text
      text: '#1a1a1a',
      textSecondary: '#6b7280',
      textTertiary: '#9ca3af',
      
      // Borders
      border: '#e5e7eb',
      borderLight: '#d1d5db',
      
      // Accents
      accent: '#10a37f',
      accentLight: '#d1fae5',
      
      // Shadows
      shadow: 'rgba(0, 0, 0, 0.05)',
      shadowMd: 'rgba(0, 0, 0, 0.08)',
      shadowLg: 'rgba(0, 0, 0, 0.1)',
      
      // Risk colors
      riskLow: { bg: '#d1fae5', border: '#6ee7b7', text: '#065f46' },
      riskMedium: { bg: '#fef3c7', border: '#fcd34d', text: '#78350f' },
      riskHigh: { bg: '#fee2e2', border: '#fca5a5', text: '#7f1d1d' },
      riskCritical: { bg: '#fecaca', border: '#f87171', text: '#7f1d1d' },
      
      // Bubble colors
      bubbleUser: '#10a37f',
      bubbleBot: '#f7f7f7',
      bubbleText: '#1a1a1a',
    },
    dark: {
      // Background
      bg: '#0f172a',
      bgSecondary: '#1e293b',
      bgTertiary: '#334155',
      
      // Text
      text: '#f1f5f9',
      textSecondary: '#cbd5e1',
      textTertiary: '#94a3b8',
      
      // Borders
      border: '#334155',
      borderLight: '#475569',
      
      // Accents
      accent: '#14b8a6',
      accentLight: '#0d9488',
      
      // Shadows
      shadow: 'rgba(0, 0, 0, 0.3)',
      shadowMd: 'rgba(0, 0, 0, 0.4)',
      shadowLg: 'rgba(0, 0, 0, 0.5)',
      
      // Risk colors
      riskLow: { bg: '#064e3b', border: '#10b981', text: '#a7f3d0' },
      riskMedium: { bg: '#713f12', border: '#fbbf24', text: '#fef3c7' },
      riskHigh: { bg: '#7f1d1d', border: '#f87171', text: '#fecaca' },
      riskCritical: { bg: '#991b1b', border: '#fca5a5', text: '#fee2e2' },
      
      // Bubble colors
      bubbleUser: '#14b8a6',
      bubbleBot: '#1e293b',
      bubbleText: '#f1f5f9',
    },
  };

  const theme = isDark ? colors.dark : colors.light;

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme, theme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
