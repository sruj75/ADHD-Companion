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
      router.push('/session');
    } else {
      // Start new dynamic planning session via backend
      try {
        const response = await startPlanningMutation.mutateAsync(ENV.DEV_USER_ID);
        if (response.success) {
          router.push('/session');
        } else {
          Alert.alert('Error', 'Failed to start session. Please try again.');
        }
      } catch (error) {
        Alert.alert('Error', 'Could not connect to backend. Please check if the server is running.');
      }
    }
  };

  const handleTalkToAI = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    router.push('/session');
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
        label: '[Ready]',
        text: 'Start Planning',
        subtext: 'Tap to begin your ADHD session',
        isTimer: false
      };
    }
  };

  const timerDisplay = getTimerDisplay();

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" />
      
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
        {dynamicStatus?.status && (
          <Text style={styles.systemInfo}>
            System: {dynamicStatus.status.system_type || 'Dynamic AI'}
          </Text>
        )}
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

        {/* OR Divider (only show when not in active session) */}
        {!hasActiveSession && (
          <Text style={styles.orText}>OR</Text>
        )}

        {/* Talk to AI Now Button */}
        <TouchableOpacity 
          style={[
            styles.aiButton,
            { opacity: isConnected ? 1 : 0.6 }
          ]}
          onPress={handleTalkToAI}
          disabled={!isConnected}
        >
          <Text style={styles.aiButtonText}>Talk to AI Now</Text>
          <Text style={styles.aiButtonSubtext}>
            {isConnected ? '(Voice Mode)' : '(Offline)'}
          </Text>
        </TouchableOpacity>

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
    backgroundColor: '#ffffff',
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
  },
  content: {
    flex: 1,
    padding: 40,
    justifyContent: 'center',
    alignItems: 'center',
    gap: 40,
  },
  sectionLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#7f8c8d',
    marginBottom: 15,
    textAlign: 'center',
  },
  sessionContainer: {
    width: '100%',
    alignItems: 'center',
  },
  sessionButton: {
    width: '100%',
    backgroundColor: '#3498db',
    padding: 25,
    borderRadius: 8,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sessionButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
    marginBottom: 5,
  },
  sessionStatusText: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
  },
  timerBox: {
    width: '100%',
    backgroundColor: '#ecf0f1',
    padding: 25,
    borderRadius: 8,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#bdc3c7',
  },
  timerLabel: {
    fontSize: 16,
    color: '#2c3e50',
    marginBottom: 10,
  },
  timerText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#e74c3c',
    fontVariant: ['tabular-nums'],
  },
  orText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#95a5a6',
    textAlign: 'center',
  },
  aiButton: {
    width: '100%',
    backgroundColor: '#2ecc71',
    padding: 25,
    borderRadius: 8,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  aiButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: 'white',
    marginBottom: 5,
  },
  aiButtonSubtext: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.8)',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  statusText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#2c3e50',
  },
  systemInfo: {
    fontSize: 14,
    color: '#7f8c8d',
    textAlign: 'center',
  },
  errorContainer: {
    width: '100%',
    padding: 20,
    backgroundColor: '#f39c12',
    borderRadius: 8,
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: '#2ecc71',
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  retryText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  timerSubtext: {
    fontSize: 14,
    color: '#7f8c8d',
    marginTop: 5,
  },
});
