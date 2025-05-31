import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  StatusBar,
  Dimensions,
  Animated,
  Alert,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import { useAPI } from '../hooks/useAPI';
import { ENV } from '../config/env';
import { Audio } from 'expo-av';

const { width, height } = Dimensions.get('window');

// Voice Mode States matching backend WebSocket states
type VoiceState = 'idle' | 'listening' | 'thinking' | 'speaking';

interface VoiceMessage {
  type: 'status' | 'transcription' | 'ai_response' | 'audio_chunk' | 'error' | 'start_listening';
  state?: VoiceState;
  message?: string;
  text?: string;
  data?: string;
  is_final?: boolean;
}

export default function AIVoiceMode() {
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [statusMessage, setStatusMessage] = useState('Tap circle to start');
  const [isConnected, setIsConnected] = useState(false);
  const [sessionId] = useState(`session_${Date.now()}`);
  const [isRecording, setIsRecording] = useState(false);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [currentAIMessage, setCurrentAIMessage] = useState<string | null>(null);
  
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const audioBufferRef = useRef<string[]>([]);
  const router = useRouter();
  
  const { useHealthCheck } = useAPI();
  const { data: healthData } = useHealthCheck();

  // Audio playback for TTS
  const playAudioChunk = async (audioData: string, isFinal: boolean) => {
    try {
      // Convert base64 to audio blob
      const binaryString = atob(audioData);
      const len = binaryString.length;
      const audioArray = new Uint8Array(len);
      for (let i = 0; i < len; i++) {
        audioArray[i] = binaryString.charCodeAt(i);
      }
      const blob = new Blob([audioArray], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);

      // Play using Expo AV for both web and native
      const { sound } = await Audio.Sound.createAsync(
        { uri: url },
        { shouldPlay: true }
      );
      sound.setOnPlaybackStatusUpdate((status: any) => {
        if (status.didJustFinish) {
          URL.revokeObjectURL(url);
          sound.unloadAsync();
        }
      });
    } catch (error) {
      console.error('Failed to play audio chunk via Expo AV:', error);
    }
  };

  // Initialize microphone access for web
  useEffect(() => {
    if (Platform.OS === 'web') {
      initializeMicrophone();
    }
  }, []);

  const initializeMicrophone = async () => {
    // Ensure secure context for getUserMedia on web
    if (Platform.OS === 'web' && typeof window !== 'undefined' && !window.isSecureContext) {
      Alert.alert(
        'Secure Context Required',
        'Voice mode requires HTTPS or localhost. Please run on localhost or use HTTPS.'
      );
      setHasPermission(false);
      setStatusMessage('Secure connection required for voice mode');
      return;
    }
    // Check existing microphone permission status
    if (navigator.permissions) {
      try {
        const status = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        console.log('Microphone permission state:', status.state);
        if (status.state === 'denied') {
          Alert.alert(
            'Microphone Permission Denied',
            'Please enable microphone access in your browser settings.'
          );
          setHasPermission(false);
          setStatusMessage('Microphone permission denied');
          return;
        }
      } catch (e) {
        console.warn('Permissions API not supported:', e);
      }
    }
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        Alert.alert('Audio Not Supported', 'Your browser does not support audio recording');
        return;
      }

      // Request microphone permission
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      
      audioStreamRef.current = stream;
      setHasPermission(true);
      setStatusMessage('Microphone ready - tap to start');
      
      // Stop the initial stream since we just needed permission
      stream.getTracks().forEach(track => track.stop());
      
    } catch (error) {
      console.error('Microphone access denied:', error);
      setHasPermission(false);
      setStatusMessage('Microphone access required for voice mode');
      Alert.alert(
        'Microphone Permission Required', 
        'Please allow microphone access to use voice mode',
        [{ text: 'OK' }]
      );
    }
  };

  // Pulsing animation for the circle
  useEffect(() => {
    const createPulseAnimation = () => {
      return Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.3,
            duration: 800,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 800,
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

  // WebSocket connection setup
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const wsUrl = `${ENV.WS_URL}/ws/voice/${sessionId}`;
        console.log('Connecting to WebSocket:', wsUrl);
        
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket connected');
          setIsConnected(true);
          if (hasPermission) {
            setStatusMessage('Ready for voice interaction');
          }
        };

        ws.onmessage = (event) => {
          try {
            const message: VoiceMessage = JSON.parse(event.data);
            console.log('Received message:', message);
            handleWebSocketMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setIsConnected(false);
          setStatusMessage('Connection error');
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
          setIsConnected(false);
          setStatusMessage('Disconnected - tap to retry');
          // Auto-reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

      } catch (error) {
        console.error('Failed to create WebSocket:', error);
        setStatusMessage('Failed to connect to voice service');
      }
    };

    // Only connect if backend is healthy
    if (healthData?.status === 'healthy') {
      connectWebSocket();
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [sessionId, healthData, hasPermission]);

  const handleWebSocketMessage = (message: VoiceMessage) => {
    console.log('WebSocket message received:', message.type, message);
    switch (message.type) {
      case 'status':
        // Clear audio buffer when AI starts speaking to ensure clean playback
        if (message.state === 'speaking') {
          audioBufferRef.current = [];
          console.log('Cleared audioBufferRef for new TTS session');
        }
        // Update state for ALL status types to prevent getting stuck
        if (message.state) {
          setVoiceState(message.state);
        }
        if (message.message) {
          setStatusMessage(message.message);
        }
        break;
        
      case 'transcription':
        // Transcription received but not displayed
        break;
        
      case 'ai_response':
        // Show AI response text, especially useful when TTS is silent/mock
        if (message.text) {
          setCurrentAIMessage(message.text);
        }
        break;
        
      case 'audio_chunk':
        // Log and buffer TTS audio chunks; play when final arrives
        console.log(`Received audio_chunk: length=${message.data?.length}, is_final=${message.is_final}`);
        if (message.data) {
          audioBufferRef.current.push(message.data);
          if (message.is_final) {
            const fullAudioData = audioBufferRef.current.join('');
            console.log('Final audio_chunk received, total buffered length:', fullAudioData.length);
            playAudioChunk(fullAudioData, true);
            // Clear buffer after playback
            audioBufferRef.current = [];
          }
        }
        break;
        
      case 'error':
        setVoiceState('idle');
        setStatusMessage(message.message || 'An error occurred');
        setCurrentAIMessage(null);
        Alert.alert('Voice Error', message.message || 'Unknown error');
        break;
        
      case 'start_listening':
        // AI finished speaking, now start recording automatically
        setVoiceState('listening');
        setStatusMessage('I\'m listening... (tap when done speaking)');
        setCurrentAIMessage(null); // Clear AI message when switching to listening
        startUserRecording();
        break;
    }
  };

  const sendWebSocketMessage = (message: any) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      Alert.alert('Connection Error', 'WebSocket is not connected');
    }
  };

  // Start voice interaction - AI speaks first, no recording yet
  const startVoiceInteraction = async () => {
    if (!isConnected) {
      Alert.alert('Not Connected', 'Please wait for connection to be established');
      return;
    }

    if (!hasPermission) {
      await initializeMicrophone();
      return;
    }

    try {
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      
      // Just send start recording message to backend - AI will speak first
      // DO NOT start audio recording yet!
      sendWebSocketMessage({
        type: 'start_recording'
      });

    } catch (error) {
      console.error('Failed to start voice interaction:', error);
      Alert.alert('Error', 'Failed to start voice interaction');
    }
  };

  // Start actual audio recording when user needs to respond
  const startUserRecording = async () => {
    if (!isConnected || !hasPermission) return;

    try {
      // Get fresh media stream for recording
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      
      audioStreamRef.current = stream;
      audioChunksRef.current = [];

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm;codecs=opus' });
        await sendAudioToBackend(audioBlob);
        
        // Clean up stream
        if (audioStreamRef.current) {
          audioStreamRef.current.getTracks().forEach(track => track.stop());
        }
      };

      // Start recording
      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      
      Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);

    } catch (error) {
      console.error('Failed to start user recording:', error);
      Alert.alert('Recording Error', 'Failed to start audio recording');
    }
  };

  // Stop voice recording and send audio data
  const stopVoiceInteraction = async () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Send audio data to backend
  const sendAudioToBackend = async (audioBlob: Blob) => {
    try {
      // Convert blob to base64 for WebSocket transmission
      const arrayBuffer = await audioBlob.arrayBuffer();
      const base64Audio = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
      
      console.log(`Sending ${audioBlob.size} bytes of ${audioBlob.type} audio to backend`);
      
      // Send audio data to backend
      sendWebSocketMessage({
        type: 'audio_data',
        data: base64Audio,
        format: audioBlob.type || 'webm',
        size: audioBlob.size
      });

    } catch (error) {
      console.error('Failed to send audio:', error);
      Alert.alert('Error', 'Failed to process audio recording');
      
      // Reset state on error
      setVoiceState('idle');
      setStatusMessage('Ready to try again');
    }
  };

  // Interrupt AI speaking
  const interruptAI = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    sendWebSocketMessage({
      type: 'interrupt'
    });
  };

  const handleCirclePress = () => {
    if (!hasPermission) {
      initializeMicrophone();
      return;
    }

    switch (voiceState) {
      case 'idle':
        startVoiceInteraction();
        break;
      case 'listening':
        stopVoiceInteraction();
        break;
      case 'speaking':
        // During AI speaking, tapping starts user recording
        startUserRecording();
        break;
      case 'thinking':
        // Do nothing during thinking state
        break;
    }
  };

  const getStatusText = () => {
    if (!hasPermission) {
      return 'Tap to enable microphone access';
    }
    
    if (!isConnected) {
      return 'Connecting to voice service...';
    }
    
    switch (voiceState) {
      case 'listening': return 'I\'m listening... (tap when done speaking)';
      case 'thinking': return 'Let me think about that...';
      case 'speaking': return 'I\'m speaking - listen carefully!';
      case 'idle': return 'Tap the circle and I\'ll start our conversation!';
      default: return statusMessage;
    }
  };

  const getStatusColor = () => {
    if (!hasPermission) return '#e74c3c';
    if (!isConnected) return '#e74c3c';
    
    switch (voiceState) {
      case 'listening': return '#3498db';
      case 'thinking': return '#f39c12';
      case 'speaking': return '#2ecc71';
      default: return '#95a5a6';
    }
  };

  const getCircleOpacity = () => {
    return (isConnected && hasPermission) ? 1 : 0.5;
  };

  const getHelpText = () => {
    if (!hasPermission) {
      return "🎤 We need access to your microphone to have voice conversations";
    }
    
    if (!isConnected) {
      return "🔄 Getting connected to your AI assistant...";
    }
    
    switch (voiceState) {
      case 'idle':
        return "👋 Ready to chat! I'll speak first when you tap the circle";
      case 'listening':
        return "👂 I'm listening carefully - tap when you're done speaking";
      case 'thinking':
        return "🤔 Processing your message and preparing my response";
      case 'speaking':
        return "🗣️ I'm responding... (if audio is silent, check the text below)";
      default:
        return "💬 Let's have a helpful conversation about your day";
    }
  };

  // Clean up on component unmount
  useEffect(() => {
    return () => {
      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (mediaRecorderRef.current && isRecording) {
        mediaRecorderRef.current.stop();
      }
    };
  }, [isRecording]);

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

      {/* Main Content - Interactive Circle */}
      <View style={styles.content}>
        <View style={styles.voiceSection}>
          
          {/* Connection Status */}
          <View style={styles.connectionStatus}>
            <View style={[
              styles.connectionDot,
              { backgroundColor: (isConnected && hasPermission) ? '#2ecc71' : '#e74c3c' }
            ]} />
            <Text style={styles.connectionText}>
              {!hasPermission ? 'Microphone access required' : 
               isConnected ? 'Connected to Voice Service' : 'Connecting...'}
            </Text>
          </View>

          {/* Interactive Voice Circle */}
          <TouchableOpacity 
            onPress={handleCirclePress}
            disabled={voiceState === 'thinking'}
            style={[styles.circleContainer, { opacity: getCircleOpacity() }]}
          >
            <Animated.View 
              style={[
                styles.pulsingCircle,
                {
                  transform: [{ scale: pulseAnim }],
                  backgroundColor: getStatusColor(),
                }
              ]}
            >
              {!hasPermission && (
                <Ionicons name="mic-off" size={48} color="white" />
              )}
              {hasPermission && voiceState === 'idle' && (
                <Ionicons name="mic" size={48} color="white" />
              )}
              {voiceState === 'listening' && (
                <Ionicons name="mic" size={48} color="white" />
              )}
              {voiceState === 'thinking' && (
                <Ionicons name="hourglass" size={48} color="white" />
              )}
              {voiceState === 'speaking' && (
                <Ionicons name="volume-high" size={48} color="white" />
              )}
            </Animated.View>
          </TouchableOpacity>
          
          {/* Status Text */}
          <Text style={[styles.statusText, { color: getStatusColor() }]}>
            {getStatusText()}
          </Text>

          {/* Help Text */}
          <Text style={styles.helpText}>
            {getHelpText()}
          </Text>

          {/* Current AI Message Display (useful when TTS is silent) */}
          {currentAIMessage && (
            <View style={styles.aiMessageContainer}>
              <Text style={styles.aiMessageLabel}>AI says:</Text>
              <Text style={styles.aiMessageText}>{currentAIMessage}</Text>
            </View>
          )}
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
    width: 40,
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  voiceSection: {
    alignItems: 'center',
    width: '100%',
  },
  connectionStatus: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 40,
  },
  connectionDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 8,
  },
  connectionText: {
    fontSize: 14,
    color: '#7f8c8d',
  },
  circleContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 30,
  },
  pulsingCircle: {
    width: 140,
    height: 140,
    borderRadius: 70,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  statusText: {
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 10,
  },
  helpText: {
    fontSize: 16,
    color: '#7f8c8d',
    textAlign: 'center',
    marginBottom: 30,
    paddingHorizontal: 20,
    lineHeight: 22,
  },
  aiMessageContainer: {
    backgroundColor: '#f8f9fa',
    borderColor: '#e9ecef',
    borderWidth: 1,
    padding: 15,
    borderRadius: 8,
    marginTop: 20,
    maxWidth: '90%',
  },
  aiMessageLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6c757d',
    marginBottom: 5,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  aiMessageText: {
    fontSize: 16,
    color: '#495057',
    lineHeight: 22,
  },
}); 