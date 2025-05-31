import { useState, useCallback } from 'react';
import axios from 'axios';

// Configuration
const API_BASE_URL = 'http://localhost:8000'; // Update this for your deployment

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

interface DynamicPlanningResponse {
  success: boolean;
  ai_question: string;
  conversation_id: number;
  system_type: string;
}

interface DynamicWorkBlockResponse {
  success: boolean;
  ai_question: string;
  duration_options: number[];
  reasoning: string;
  awaiting_user_choice: boolean;
}

interface DynamicStateCheckResponse {
  success: boolean;
  adaptation_response: {
    emotional_state_detected: string;
    needs_adaptation: boolean;
    suggested_action: string;
    ai_response: string;
    reasoning: string;
  };
  current_work_context?: any;
}

export const useAPI = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiCall = useCallback(async <T>(
    endpoint: string, 
    method: 'GET' | 'POST' = 'GET', 
    data?: any
  ): Promise<ApiResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios({
        method,
        url: `${API_BASE_URL}${endpoint}`,
        data,
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000, // 10 second timeout
      });

      setLoading(false);
      return {
        success: true,
        data: response.data,
      };
    } catch (err: any) {
      setLoading(false);
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage,
      };
    }
  }, []);

  // Specific API methods for the dynamic system
  const startDynamicPlanning = useCallback(async (userId: number) => {
    return apiCall<DynamicPlanningResponse>('/api/dynamic/planning/start', 'POST', { user_id: userId });
  }, [apiCall]);

  const continueDynamicPlanning = useCallback(async (userId: number, userResponse: string) => {
    return apiCall('/api/dynamic/planning/continue', 'POST', { 
      user_id: userId, 
      user_response: userResponse 
    });
  }, [apiCall]);

  const startDynamicWorkBlock = useCallback(async (userId: number, taskDescription: string = '') => {
    return apiCall<DynamicWorkBlockResponse>('/api/dynamic/work-block/start', 'POST', { 
      user_id: userId, 
      task_description: taskDescription 
    });
  }, [apiCall]);

  const confirmWorkBlockDuration = useCallback(async (userId: number, chosenDuration: number) => {
    return apiCall('/api/dynamic/work-block/confirm', 'POST', { 
      user_id: userId, 
      chosen_duration: chosenDuration 
    });
  }, [apiCall]);

  const dynamicStateCheck = useCallback(async (userId: number, userMessage: string) => {
    return apiCall<DynamicStateCheckResponse>('/api/dynamic/state-check', 'POST', { 
      user_id: userId, 
      user_message: userMessage 
    });
  }, [apiCall]);

  const getDynamicStatus = useCallback(async (userId: number) => {
    return apiCall(`/api/dynamic/status/${userId}`);
  }, [apiCall]);

  const healthCheck = useCallback(async () => {
    return apiCall('/health');
  }, [apiCall]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    clearError,
    // Generic API call
    apiCall,
    // Specific dynamic system endpoints
    startDynamicPlanning,
    continueDynamicPlanning,
    startDynamicWorkBlock,
    confirmWorkBlockDuration,
    dynamicStateCheck,
    getDynamicStatus,
    healthCheck,
  };
}; 