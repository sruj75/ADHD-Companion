import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  Dimensions,
  Animated,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';

const { width, height } = Dimensions.get('window');

// Voice Mode States
type VoiceState = 'listening' | 'thinking' | 'speaking' | 'idle';

export default function AIVoiceMode() {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const router = useRouter();

  // Pulsing animation for the circle
  useEffect(() => {
    const createPulseAnimation = () => {
      return Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 1000,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 1000,
            useNativeDriver: true,
          }),
        ])
      );
    };

    let animation: Animated.CompositeAnimation;
    
    if (voiceState === 'listening' || voiceState === 'thinking') {
      animation = createPulseAnimation();
      animation.start();
    }

    return () => {
      if (animation) {
        animation.stop();
      }
    };
  }, [voiceState, pulseAnim]);

  // Mock voice interaction simulation
  const simulateVoiceInteraction = async () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    
    // Simulate listening
    setVoiceState('listening');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Simulate thinking
    setVoiceState('thinking');
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Simulate speaking
    setVoiceState('speaking');
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    setVoiceState('idle');
  };

  const getStatusText = () => {
    switch (voiceState) {
      case 'listening': return 'Status: Listening';
      case 'thinking': return 'Status: Thinking';
      case 'speaking': return 'Status: Speaking';
      default: return 'Tap circle to start';
    }
  };

  const getStatusColor = () => {
    switch (voiceState) {
      case 'listening': return '#3498db';
      case 'thinking': return '#f39c12';
      case 'speaking': return '#2ecc71';
      default: return '#95a5a6';
    }
  };

  return (
    <View style={styles.container}>
      <StatusBar barStyle="dark-content" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton} 
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#2c3e50" />
        </TouchableOpacity>
        <Text style={styles.title}>AI Voice Mode</Text>
        <View style={styles.spacer} />
      </View>

      {/* Main Content - Just the Circle */}
      <View style={styles.content}>
        <View style={styles.voiceSection}>
          <TouchableOpacity 
            onPress={simulateVoiceInteraction}
            disabled={voiceState !== 'idle'}
            style={styles.circleContainer}
          >
            <Animated.View 
              style={[
                styles.pulsingCircle,
                {
                  transform: [{ scale: pulseAnim }],
                  backgroundColor: getStatusColor(),
                }
              ]}
            />
          </TouchableOpacity>
          
          {/* Status Text */}
          <Text style={[styles.statusText, { color: getStatusColor() }]}>
            {getStatusText()}
          </Text>
        </View>
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
    flexDirection: 'row',
    alignItems: 'center',
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  backButton: {
    padding: 8,
    marginRight: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2c3e50',
    textAlign: 'center',
    flex: 1,
  },
  spacer: {
    width: 40, // Balance the back button
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  voiceSection: {
    alignItems: 'center',
  },
  circleContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  pulsingCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  statusText: {
    fontSize: 18,
    fontWeight: '600',
    marginTop: 30,
    textAlign: 'center',
  },
}); 