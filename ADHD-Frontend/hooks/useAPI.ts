import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ADHDApiService } from '../config/api';
import { ENV } from '../config/env';

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

// React Query Keys
export const QUERY_KEYS = {
  health: ['health'],
  dynamicStatus: (userId: number) => ['dynamicStatus', userId],
  userSessions: (userId: number) => ['userSessions', userId],
  userStats: (userId: number) => ['userStats', userId],
  voiceModels: ['voiceModels'],
  availableVoices: ['availableVoices'],
} as const;

export const useAPI = () => {
  const [error, setError] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Health Check Query
  const useHealthCheck = () => {
    return useQuery({
      queryKey: QUERY_KEYS.health,
      queryFn: ADHDApiService.healthCheck,
      refetchInterval: 30000, // Refetch every 30 seconds
    });
  };

  // Dynamic Status Query
  const useDynamicStatus = (userId: number = ENV.DEV_USER_ID) => {
    return useQuery({
      queryKey: QUERY_KEYS.dynamicStatus(userId),
      queryFn: () => ADHDApiService.getDynamicStatus(userId),
      refetchInterval: 10000, // Refetch every 10 seconds for real-time updates
    });
  };

  // Voice Models Query
  const useVoiceModels = () => {
    return useQuery({
      queryKey: QUERY_KEYS.voiceModels,
      queryFn: ADHDApiService.getVoiceModels,
      staleTime: 5 * 60 * 1000, // 5 minutes
    });
  };

  // Session Management Mutations
  const useCreateSession = () => {
    return useMutation({
      mutationFn: ({ 
        userId, 
        sessionType, 
        scheduledTime 
      }: { 
        userId: number; 
        sessionType: string; 
        scheduledTime?: string; 
      }) => 
        ADHDApiService.createSession(userId, sessionType, scheduledTime),
      onSuccess: () => {
        // Invalidate related queries
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.userSessions(ENV.DEV_USER_ID) });
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dynamicStatus(ENV.DEV_USER_ID) });
      },
    });
  };

  const useSendMessage = () => {
    return useMutation({
      mutationFn: ({ sessionId, message }: { sessionId: number; message: string }) =>
        ADHDApiService.sendMessage(sessionId, message),
    });
  };

  // Dynamic Planning Mutations
  const useStartDynamicPlanning = () => {
    return useMutation({
      mutationFn: (userId: number = ENV.DEV_USER_ID) =>
        ADHDApiService.startDynamicPlanning(userId),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dynamicStatus(ENV.DEV_USER_ID) });
      },
    });
  };

  const useContinueDynamicPlanning = () => {
    return useMutation({
      mutationFn: ({ userId, userResponse }: { userId: number; userResponse: string }) =>
        ADHDApiService.continueDynamicPlanning(userId, userResponse),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dynamicStatus(ENV.DEV_USER_ID) });
      },
    });
  };

  const useStartDynamicWorkBlock = () => {
    return useMutation({
      mutationFn: ({ userId, taskDescription }: { userId: number; taskDescription?: string }) =>
        ADHDApiService.startDynamicWorkBlock(userId, taskDescription || ''),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dynamicStatus(ENV.DEV_USER_ID) });
      },
    });
  };

  const useConfirmWorkBlockDuration = () => {
    return useMutation({
      mutationFn: ({ userId, duration }: { userId: number; duration: number }) =>
        ADHDApiService.confirmWorkBlockDuration(userId, duration),
      onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: QUERY_KEYS.dynamicStatus(ENV.DEV_USER_ID) });
      },
    });
  };

  const useDynamicStateCheck = () => {
    return useMutation({
      mutationFn: ({ userId, message }: { userId: number; message: string }) =>
        ADHDApiService.dynamicStateCheck(userId, message),
    });
  };

  // Voice Integration Queries
  const useAvailableVoices = () => {
    return useQuery({
      queryKey: QUERY_KEYS.availableVoices,
      queryFn: ADHDApiService.getAvailableVoices,
      staleTime: 10 * 60 * 1000, // 10 minutes
    });
  };

  // Generic API call function (for custom endpoints)
  const apiCall = useCallback(async <T>(
    endpoint: string, 
    method: 'GET' | 'POST' = 'GET', 
    data?: any
  ): Promise<ApiResponse<T>> => {
    setError(null);

    try {
      const response = method === 'GET' 
        ? await ADHDApiService.healthCheck() // Replace with generic call if needed
        : await ADHDApiService.sendChatMessage(data?.text || '');

      return {
        success: true,
        data: response,
      };
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'An error occurred';
      setError(errorMessage);
      return {
        success: false,
        error: errorMessage,
      };
    }
  }, []);

  return {
    // State
    error,
    clearError,
    
    // Queries
    useHealthCheck,
    useDynamicStatus,
    useVoiceModels,
    useAvailableVoices,
    
    // Mutations
    useCreateSession,
    useSendMessage,
    useStartDynamicPlanning,
    useContinueDynamicPlanning,
    useStartDynamicWorkBlock,
    useConfirmWorkBlockDuration,
    useDynamicStateCheck,
    
    // Utilities
    apiCall,
  };
}; 