import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  Dimensions,
  Alert,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import { useAPI } from '../hooks/useAPI';
import { ENV } from '../config/env';

const { width, height } = Dimensions.get('window');

// LAYERED LOGIC:
// 1. If there are active sessions -> show [Active Session] 
// 2. If no active sessions -> show [Timer Mode] with real countdown from backend
// 3. Always show "Talk to AI Now" as override option

export default function AdaptiveDashboard() {
  const router = useRouter();
  const { useDynamicStatus, useHealthCheck, useStartDynamicPlanning } = useAPI();

  // Get real-time data from backend
  const { 
    data: healthData, 
    isLoading: healthLoading, 
    error: healthError 
  } = useHealthCheck();

  const { 
    data: dynamicStatus, 
    isLoading: statusLoading, 
    error: statusError,
    refetch: refetchStatus
  } = useDynamicStatus(ENV.DEV_USER_ID);

  const startPlanningMutation = useStartDynamicPlanning();

  // Local countdown state (only used when backend provides next session time)
  const [localCountdown, setLocalCountdown] = useState<number | null>(null);

  // Extract REAL session state from backend data
  const hasActiveSession = dynamicStatus?.status?.has_active_conversation || 
                          (dynamicStatus?.status?.active_work_blocks?.length > 0);
  
  // Use real backend timer or show "Ready to start"
  const backendSessionTime = dynamicStatus?.status?.next_session_time;
  const sessionType = dynamicStatus?.status?.conversation_state || "Dynamic Planning";

  // Real-time countdown from backend data
  useEffect(() => {
    if (typeof backendSessionTime === 'number' && backendSessionTime > 0) {
      setLocalCountdown(backendSessionTime);
    } else {
      setLocalCountdown(null); // No active timer
    }
  }, [backendSessionTime]);

  // Only run countdown if we have a real timer from backend
  useEffect(() => {
    if (localCountdown && localCountdown > 0 && !hasActiveSession) {
      const interval = setInterval(() => {
        setLocalCountdown(prev => {
          if (prev && prev > 1) {
            return prev - 1;
          } else {
            // Timer finished - trigger backend to start session
            refetchStatus();
            return 0;
          }
        });
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [localCountdown, hasActiveSession, refetchStatus]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${String(secs).padStart(2, '0')}`;
  };

  const handleStartSession = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    if (hasActiveSession) {
      // Navigate to existing session
      router.push('./chat');
    } else {
      // Start new dynamic planning session via backend
      try {
        const response = await startPlanningMutation.mutateAsync(ENV.DEV_USER_ID);
        if (response.success) {
          router.push('./chat');
        } else {
          Alert.alert('Error', 'Failed to start session. Please try again.');
        }
      } catch (error) {
        Alert.alert('Error', 'Could not connect to backend. Please check if the server is running.');
      }
    }
  };

  // Show connection status
  const isConnected = healthData?.status === 'healthy';
  const isLoading = healthLoading || statusLoading;

  // Determine what to show in timer section
  const getTimerDisplay = () => {
    if (hasActiveSession) {
      return {
        label: '[Active Session]',
        text: 'Continue Session',
        subtext: `${sessionType} (Active)`,
        isTimer: false
      };
    } else if (localCountdown && localCountdown > 0) {
      return {
        label: '[Timer Mode]',
        text: formatTime(localCountdown),
        subtext: 'Next session starting automatically',
        isTimer: true
      };
    } else {
      return {
        label: '',
        text: 'Start Planning',
        subtext: 'Tap to begin your ADHD session',
        isTimer: false
      };
    }
  };

  const timerDisplay = getTimerDisplay();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0f0f1a" />
      
      {/* Header with Connection Status */}
      <View style={styles.header}>
        <Text style={styles.title}>ADHD Companion</Text>
        <View style={styles.statusRow}>
          <View style={[
            styles.statusDot, 
            { backgroundColor: isConnected ? '#2ecc71' : '#e74c3c' }
          ]} />
          <Text style={[
            styles.statusText,
            { color: isConnected ? '#2ecc71' : '#e74c3c' }
          ]}>
            {isLoading ? 'Connecting...' : isConnected ? 'Connected' : 'Offline'}
          </Text>
        </View>
      </View>

      <View style={styles.content}>
        
        {/* Dynamic Session State */}
        <View style={styles.sessionContainer}>
          <Text style={styles.sectionLabel}>{timerDisplay.label}</Text>
          <TouchableOpacity 
            style={[
              timerDisplay.isTimer ? styles.timerBox : styles.sessionButton,
              !isConnected && { opacity: 0.6 }
            ]}
            onPress={handleStartSession}
            disabled={startPlanningMutation.isPending || !isConnected}
          >
            <Text style={timerDisplay.isTimer ? styles.timerLabel : styles.sessionButtonText}>
              {startPlanningMutation.isPending ? 'Starting...' : timerDisplay.text}
            </Text>
            {timerDisplay.isTimer ? (
              <Text style={styles.timerText}>{timerDisplay.text}</Text>
            ) : null}
            <Text style={timerDisplay.isTimer ? styles.timerSubtext : styles.sessionStatusText}>
              {timerDisplay.subtext}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Error Display */}
        {(healthError || statusError) && (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>
              ⚠️ {healthError?.message || statusError?.message || 'Connection issue'}
            </Text>
            <TouchableOpacity 
              style={styles.retryButton}
              onPress={() => refetchStatus()}
            >
              <Text style={styles.retryText}>Retry</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1a', // Deep dark background
  },
  header: {
    paddingTop: 60,
    paddingBottom: 25,
    paddingHorizontal: 20,
    backgroundColor: 'rgba(20, 20, 35, 0.95)', // Semi-transparent dark header
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(99, 102, 241, 0.2)', // Subtle purple border
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#ffffff',
    textAlign: 'center',
    marginBottom: 10,
  },
  content: {
    flex: 1,
    padding: 40,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 35,
  },
  sectionLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#a5a5d6', // Soft purple-gray
    marginBottom: 20,
    textAlign: 'center',
    letterSpacing: 0.5,
  },
  sessionContainer: {
    width: '100%',
    alignItems: 'center',
  },
  sessionButton: {
    width: '100%',
    backgroundColor: '#5b6cf7', // Beautiful blue-purple
    padding: 30,
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#5b6cf7',
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 8,
  },
  sessionButtonText: {
    fontSize: 20,
    fontWeight: '700',
    color: '#ffffff',
    marginBottom: 8,
    letterSpacing: 0.3,
  },
  sessionStatusText: {
    fontSize: 15,
    color: 'rgba(255,255,255,0.85)',
    fontWeight: '500',
  },
  timerBox: {
    width: '100%',
    backgroundColor: 'rgba(31, 31, 50, 0.8)', // Dark semi-transparent
    padding: 30,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.3)', // Purple border
    shadowColor: '#8b5cf6',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 12,
    elevation: 4,
  },
  timerLabel: {
    fontSize: 18,
    color: '#c7c7e8',
    marginBottom: 15,
    fontWeight: '600',
  },
  timerText: {
    fontSize: 42,
    fontWeight: 'bold',
    color: '#ff6b9d', // Bright pink for timer
    fontVariant: ['tabular-nums'],
    textShadowColor: 'rgba(255, 107, 157, 0.3)',
    textShadowOffset: { width: 0, height: 2 },
    textShadowRadius: 8,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginTop: 5,
  },
  statusDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.5,
    shadowRadius: 4,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  systemInfo: {
    fontSize: 14,
    color: '#9ca3d4',
    textAlign: 'center',
    marginTop: 8,
    fontStyle: 'italic',
  },
  errorContainer: {
    width: '100%',
    padding: 25,
    backgroundColor: 'rgba(239, 68, 68, 0.15)', // Semi-transparent red
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.3)',
  },
  errorText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fca5a5', // Light red
    marginBottom: 20,
    textAlign: 'center',
  },
  retryButton: {
    backgroundColor: '#10b981', // Green
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: 'center',
    shadowColor: '#10b981',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  retryText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  timerSubtext: {
    fontSize: 15,
    color: '#a5a5d6',
    marginTop: 8,
    fontWeight: '500',
  },
});
