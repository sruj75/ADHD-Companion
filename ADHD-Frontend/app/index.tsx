import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  Dimensions,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';

const { width, height } = Dimensions.get('window');

// Mock session state - replace with real API
const mockSessionState = {
  hasActiveSession: false, // Toggle this to show different states
  nextSessionTime: 25 * 60 + 30, // 25:30 in seconds - TODO: Make this dynamic from backend
  sessionType: "Morning Planning"
};

// LAYERED LOGIC:
// 1. If there are active sessions -> show [Active Session] 
// 2. If no active sessions -> show [Timer Mode] with countdown
// 3. Always show "Talk to AI Now" as override option

export default function AdaptiveDashboard() {
  const [timeRemaining, setTimeRemaining] = useState(mockSessionState.nextSessionTime);
  const [hasActiveSession, setHasActiveSession] = useState(mockSessionState.hasActiveSession);
  const router = useRouter();

  // Countdown timer for next session
  useEffect(() => {
    if (!hasActiveSession && timeRemaining > 0) {
      const interval = setInterval(() => {
        setTimeRemaining(prev => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [hasActiveSession, timeRemaining]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${String(secs).padStart(2, '0')}`;
  };

  const handleStartSession = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setHasActiveSession(true);
    router.push('/session');
  };

  const handleTalkToAI = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    router.push('/session');
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" />
      
      {/* Simple Header */}
      <View style={styles.header}>
        <Text style={styles.title}>ADHD Companion</Text>
      </View>

      <View style={styles.content}>
        
        {/* Active Session OR Timer Mode */}
        {hasActiveSession ? (
          // Active Session State
          <View style={styles.sessionContainer}>
            <Text style={styles.sectionLabel}>[Active Session]</Text>
            <TouchableOpacity 
              style={styles.sessionButton}
              onPress={handleStartSession}
            >
              <Text style={styles.sessionButtonText}>Start Session</Text>
              <Text style={styles.sessionStatusText}>(Available)</Text>
            </TouchableOpacity>
          </View>
        ) : (
          // Timer Mode State
          <View style={styles.sessionContainer}>
            <Text style={styles.sectionLabel}>[Timer Mode]</Text>
            <View style={styles.timerBox}>
              <Text style={styles.timerLabel}>Next Session In</Text>
              <Text style={styles.timerText}>{formatTime(timeRemaining)}</Text>
            </View>
          </View>
        )}

        {/* OR Divider (only show when in timer mode) */}
        {!hasActiveSession && (
          <Text style={styles.orText}>OR</Text>
        )}

        {/* Talk to AI Now Button */}
        <TouchableOpacity 
          style={styles.aiButton}
          onPress={handleTalkToAI}
        >
          <Text style={styles.aiButtonText}>Talk to AI Now</Text>
          <Text style={styles.aiButtonSubtext}>(Override)</Text>
        </TouchableOpacity>
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
});
