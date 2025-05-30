import axios from 'axios';

// API base URL - change this to your backend URL
const BASE_URL = __DEV__ 
  ? 'http://localhost:8000'  // Development
  : 'https://your-backend-url.com';  // Production

// Create axios instance
export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const endpoints = {
  root: '/',
  chat: '/chat',
} as const;

// API functions
export const apiService = {
  // Test connection to backend
  testConnection: () => api.get(endpoints.root),
  
  // Send message to AI chat
  sendMessage: (text: string) => 
    api.post(endpoints.chat, { text }),
}; 