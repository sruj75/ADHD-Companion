import React, { useState, useEffect, useRef } from 'react';
import { 
  Text, 
  View, 
  StyleSheet, 
  TouchableOpacity, 
  Animated,
  Alert,
  Dimensions 
} from 'react-native';
import * as Speech from 'expo-speech';
import { Audio } from 'expo-av';
import { apiService } from '../config/api';

// Get screen dimensions for responsive design
const { width, height } = Dimensions.get('window');

// Voice agent states
type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

export default function VoiceAgent() {
  // State management
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [transcript, setTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  
  // Animation references
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const glowAnim = useRef(new Animated.Value(0)).current;
  
  // Audio recording reference
  const recording = useRef<Audio.Recording | null>(null);

  // Set up audio permissions and configuration
  useEffect(() => {
    setupAudio();
  }, []);

  // Animation effects based on voice state
  useEffect(() => {
    startAnimation();
  }, [voiceState]);

  const setupAudio = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        Alert.alert('Permission needed', 'Please grant microphone permission to use voice features');
        return;
      }
      
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
    } catch (error) {
      console.error('Audio setup failed:', error);
    }
  };

  // Pulse animation for different states
  const startAnimation = () => {
    // Stop any existing animations
    pulseAnim.stopAnimation();
    glowAnim.stopAnimation();

    switch (voiceState) {
      case 'listening':
        // Fast pulse for listening
        Animated.loop(
          Animated.sequence([
            Animated.timing(pulseAnim, {
              toValue: 1.3,
              duration: 600,
              useNativeDriver: true,
            }),
            Animated.timing(pulseAnim, {
              toValue: 1,
              duration: 600,
              useNativeDriver: true,
            }),
          ])
        ).start();
        
        // Glow effect
        Animated.loop(
          Animated.sequence([
            Animated.timing(glowAnim, {
              toValue: 1,
              duration: 1000,
              useNativeDriver: true,
            }),
            Animated.timing(glowAnim, {
              toValue: 0,
              duration: 1000,
              useNativeDriver: true,
            }),
          ])
        ).start();
        break;

      case 'processing':
        // Slow continuous pulse for thinking
        Animated.loop(
          Animated.timing(pulseAnim, {
            toValue: 1.1,
            duration: 1500,
            useNativeDriver: true,
          })
        ).start();
        break;

      case 'speaking':
        // Quick pulse for speaking
        Animated.loop(
          Animated.sequence([
            Animated.timing(pulseAnim, {
              toValue: 1.2,
              duration: 400,
              useNativeDriver: true,
            }),
            Animated.timing(pulseAnim, {
              toValue: 1,
              duration: 400,
              useNativeDriver: true,
            }),
          ])
        ).start();
        break;

      default:
        // Reset to normal state
        Animated.timing(pulseAnim, {
          toValue: 1,
          duration: 300,
          useNativeDriver: true,
        }).start();
        
        Animated.timing(glowAnim, {
          toValue: 0,
          duration: 300,
          useNativeDriver: true,
        }).start();
    }
  };

  // Start voice recording
  const startListening = async () => {
    try {
      setVoiceState('listening');
      setTranscript('Listening...');
      
      // For now, we'll simulate speech recognition
      // In a real app, you'd use a speech recognition service
      simulateSpeechRecognition();
      
    } catch (error) {
      console.error('Failed to start listening:', error);
      setVoiceState('idle');
    }
  };

  // Simulate speech recognition (replace with real STT)
  const simulateSpeechRecognition = () => {
    setTimeout(() => {
      const sampleText = "Help me focus on my daily tasks";
      setTranscript(sampleText);
      processUserInput(sampleText);
    }, 3000);
  };

  // Process user input and get AI response
  const processUserInput = async (userText: string) => {
    try {
      setVoiceState('processing');
      setAiResponse('Thinking...');

      // Send to your FastAPI backend
      const response = await apiService.sendMessage(userText);
      
      if (response.data.response) {
        setAiResponse(response.data.response);
        speakResponse(response.data.response);
      } else {
        throw new Error('No response from AI');
      }
      
    } catch (error) {
      console.error('Failed to process input:', error);
      const fallbackResponse = "I'm having trouble connecting right now. Please try again.";
      setAiResponse(fallbackResponse);
      speakResponse(fallbackResponse);
    }
  };

  // Text-to-Speech for AI responses
  const speakResponse = (text: string) => {
    setVoiceState('speaking');
    
    Speech.speak(text, {
      voice: 'com.apple.ttsbundle.Samantha-compact', // iOS voice
      rate: 0.9,
      pitch: 1.0,
      onDone: () => {
        setVoiceState('idle');
      },
      onError: (error) => {
        console.error('TTS Error:', error);
        setVoiceState('idle');
      }
    });
  };

  // Stop current action
  const stopAction = () => {
    Speech.stop();
    setVoiceState('idle');
    setTranscript('');
    setAiResponse('');
  };

  // Get circle color based on state
  const getCircleColor = () => {
    switch (voiceState) {
      case 'listening': return '#4ECDC4'; // Teal for listening
      case 'processing': return '#FFE66D'; // Yellow for thinking
      case 'speaking': return '#FF6B6B'; // Red for speaking
      default: return '#A8E6CF'; // Light green for idle
    }
  };

  // Get status text
  const getStatusText = () => {
    switch (voiceState) {
      case 'listening': return 'Listening...';
      case 'processing': return 'Thinking...';
      case 'speaking': return 'Speaking...';
      default: return 'Tap to start conversation';
    }
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.title}>ADHD Voice Assistant</Text>
        <Text style={styles.subtitle}>Your AI companion for focus and productivity</Text>
      </View>

      {/* Voice Circle */}
      <View style={styles.voiceContainer}>
        <Animated.View
          style={[
            styles.glowRing,
            {
              opacity: glowAnim,
              backgroundColor: getCircleColor(),
            }
          ]}
        />
        
        <TouchableOpacity
          style={[styles.voiceButton, { backgroundColor: getCircleColor() }]}
          onPress={voiceState === 'idle' ? startListening : stopAction}
          activeOpacity={0.8}
        >
          <Animated.View
            style={[
              styles.voiceButtonInner,
              {
                transform: [{ scale: pulseAnim }],
              }
            ]}
          >
            <Text style={styles.voiceButtonText}>
              {voiceState === 'idle' ? '🎤' : '⏹️'}
            </Text>
          </Animated.View>
        </TouchableOpacity>
      </View>

      {/* Status */}
      <Text style={styles.statusText}>{getStatusText()}</Text>

      {/* Conversation Display */}
      <View style={styles.conversationContainer}>
        {transcript ? (
          <View style={styles.messageContainer}>
            <Text style={styles.messageLabel}>You said:</Text>
            <Text style={styles.userMessage}>{transcript}</Text>
          </View>
        ) : null}
        
        {aiResponse ? (
          <View style={styles.messageContainer}>
            <Text style={styles.messageLabel}>AI Assistant:</Text>
            <Text style={styles.aiMessage}>{aiResponse}</Text>
          </View>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 50,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#7F8C8D',
    textAlign: 'center',
  },
  voiceContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 30,
  },
  glowRing: {
    position: 'absolute',
    width: 200,
    height: 200,
    borderRadius: 100,
    opacity: 0.3,
  },
  voiceButton: {
    width: 150,
    height: 150,
    borderRadius: 75,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  voiceButtonInner: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  voiceButtonText: {
    fontSize: 40,
  },
  statusText: {
    fontSize: 18,
    color: '#34495E',
    marginBottom: 30,
    fontWeight: '500',
  },
  conversationContainer: {
    flex: 1,
    width: '100%',
    maxWidth: 400,
  },
  messageContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  messageLabel: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#7F8C8D',
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  userMessage: {
    fontSize: 16,
    color: '#2C3E50',
    lineHeight: 22,
  },
  aiMessage: {
    fontSize: 16,
    color: '#27AE60',
    lineHeight: 22,
  },
});
