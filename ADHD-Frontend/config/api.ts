import axios, { AxiosInstance } from 'axios';
import { ENV } from './env';

// Create axios instance with proper configuration
export const api: AxiosInstance = axios.create({
  baseURL: ENV.API_URL,
  timeout: ENV.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Response Types
interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

interface SessionResponse {
  session_id: number;
  session_type: string;
  status: string;
  ai_starter_message: string;
  estimated_duration?: number;
}

interface DynamicPlanningResponse {
  success: boolean;
  ai_question: string;
  conversation_id: number;
  system_type: string;
}

// API Service with all backend endpoints
export class ADHDApiService {
  
  // Health and Status
  static async healthCheck(): Promise<any> {
    const response = await api.get('/health');
    return response.data;
  }

  static async getRoot(): Promise<any> {
    const response = await api.get('/');
    return response.data;
  }

  // Session Management
  static async createSession(
    userId: number, 
    sessionType: string, 
    scheduledTime?: string
  ): Promise<SessionResponse> {
    const response = await api.post('/api/sessions/create', {
      user_id: userId,
      session_type: sessionType,
      scheduled_time: scheduledTime,
    });
    return response.data;
  }

  static async getSession(sessionId: number): Promise<any> {
    const response = await api.get(`/api/sessions/${sessionId}`);
    return response.data;
  }

  static async startSession(sessionId: number): Promise<any> {
    const response = await api.post(`/api/sessions/${sessionId}/start`);
    return response.data;
  }

  static async sendMessage(sessionId: number, userMessage: string): Promise<any> {
    const response = await api.post(`/api/sessions/${sessionId}/message`, {
      user_message: userMessage,
    });
    return response.data;
  }

  // Dynamic AI System
  static async startDynamicPlanning(userId: number): Promise<DynamicPlanningResponse> {
    const response = await api.post('/api/dynamic/planning/start', {
      user_id: userId,
    });
    return response.data;
  }

  static async continueDynamicPlanning(userId: number, userResponse: string): Promise<any> {
    const response = await api.post('/api/dynamic/planning/continue', {
      user_id: userId,
      user_response: userResponse,
    });
    return response.data;
  }

  static async startDynamicWorkBlock(userId: number, taskDescription: string = ''): Promise<any> {
    const response = await api.post('/api/dynamic/work-block/start', {
      user_id: userId,
      task_description: taskDescription,
    });
    return response.data;
  }

  static async confirmWorkBlockDuration(userId: number, chosenDuration: number): Promise<any> {
    const response = await api.post('/api/dynamic/work-block/confirm', {
      user_id: userId,
      chosen_duration: chosenDuration,
    });
    return response.data;
  }

  static async dynamicStateCheck(userId: number, userMessage: string): Promise<any> {
    const response = await api.post('/api/dynamic/state-check', {
      user_id: userId,
      user_message: userMessage,
    });
    return response.data;
  }

  static async getDynamicStatus(userId: number): Promise<any> {
    const response = await api.get(`/api/dynamic/status/${userId}`);
    return response.data;
  }

  // User Analytics  
  static async getUserSessions(
    userId: number, 
    status?: string, 
    sessionType?: string, 
    limit: number = 20
  ): Promise<any> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (sessionType) params.append('session_type', sessionType);
    params.append('limit', limit.toString());
    
    const response = await api.get(`/api/users/${userId}/sessions?${params}`);
    return response.data;
  }

  static async getUserStatistics(userId: number, days: number = 30): Promise<any> {
    const response = await api.get(`/api/users/${userId}/statistics?days=${days}`);
    return response.data;
  }

  // Chat Messaging
  static async sendChatMessage(text: string, userId: number = 1): Promise<any> {
    const response = await api.post('/api/chat', { 
      text: text,
      user_id: userId 
    });
    return response.data;
  }
}

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
); 