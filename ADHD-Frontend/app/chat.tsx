import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  StatusBar,
  Dimensions,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import { useRouter } from 'expo-router';
import { useAPI } from '../hooks/useAPI';
import { ENV } from '../config/env';

const { width, height } = Dimensions.get('window');

interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isLoading?: boolean;
}

export default function ChatSession() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  const scrollViewRef = useRef<ScrollView>(null);
  const inputRef = useRef<TextInput>(null);
  const router = useRouter();
  
  const { 
    useHealthCheck, 
    useDynamicStatus,
    useSendChatMessage,
    useDynamicStateCheck
  } = useAPI();

  const { data: healthData } = useHealthCheck();
  const { data: dynamicStatus } = useDynamicStatus(ENV.DEV_USER_ID);
  
  const chatMutation = useSendChatMessage();
  const stateCheckMutation = useDynamicStateCheck();

  useEffect(() => {
    setIsConnected(healthData?.status === 'healthy');
  }, [healthData]);

  // Add initial AI greeting when component loads
  useEffect(() => {
    if (isConnected && messages.length === 0) {
      const greeting = getInitialGreeting();
      setMessages([{
        id: 'initial-' + Date.now(),
        text: greeting,
        sender: 'ai',
        timestamp: new Date()
      }]);
    }
  }, [isConnected, messages.length]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollViewRef.current?.scrollToEnd({ animated: true });
  }, [messages]);

  const getInitialGreeting = () => {
    const hasActiveSession = dynamicStatus?.status?.has_active_conversation;
    const sessionType = dynamicStatus?.status?.conversation_state;
    
    if (hasActiveSession) {
      return `Welcome back! Let's continue your ${sessionType || 'session'}. How are you feeling right now?`;
    } else {
      return "Hello! I'm your ADHD companion. I'm here to help you plan your tasks, manage your time, and support you through your day. What would you like to work on today?";
    }
  };

  const sendMessage = async () => {
    if (!inputText.trim() || isLoading || !isConnected) return;

    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);

    const userMessage: ChatMessage = {
      id: 'user-' + Date.now(),
      text: inputText.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    const loadingMessage: ChatMessage = {
      id: 'loading-' + Date.now(),
      text: 'AI is thinking...',
      sender: 'ai',
      timestamp: new Date(),
      isLoading: true
    };

    // Add user message and loading indicator
    setMessages(prev => [...prev, userMessage, loadingMessage]);
    setInputText('');
    setIsLoading(true);

    try {
      // Use the simple chat endpoint
      const response = await chatMutation.mutateAsync({
        text: userMessage.text,
        userId: ENV.DEV_USER_ID
      });

      // Remove loading message and add AI response
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        const aiResponse: ChatMessage = {
          id: 'ai-' + Date.now(),
          text: response?.ai_response || 'I understand. Let me help you with that.',
          sender: 'ai',
          timestamp: new Date()
        };
        return [...withoutLoading, aiResponse];
      });

    } catch (error) {
      console.error('Chat error:', error);
      
      // Remove loading message and add error message
      setMessages(prev => {
        const withoutLoading = prev.filter(msg => !msg.isLoading);
        const errorMessage: ChatMessage = {
          id: 'error-' + Date.now(),
          text: 'Sorry, I encountered an error. Please try again or check your connection.',
          sender: 'ai',
          timestamp: new Date()
        };
        return [...withoutLoading, errorMessage];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: any) => {
    if (event.nativeEvent.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    setMessages([]);
    // Add fresh greeting
    setTimeout(() => {
      const greeting = getInitialGreeting();
      setMessages([{
        id: 'clear-' + Date.now(),
        text: greeting,
        sender: 'ai',
        timestamp: new Date()
      }]);
    }, 100);
  };

  const renderMessage = (message: ChatMessage) => {
    const isUser = message.sender === 'user';
    
    return (
      <View 
        key={message.id} 
        style={[
          styles.messageContainer,
          isUser ? styles.userMessageContainer : styles.aiMessageContainer
        ]}
      >
        <View style={[
          styles.messageContent,
          isUser ? styles.userMessage : styles.aiMessage
        ]}>
          {message.isLoading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="small" color="#3498db" />
              <Text style={styles.loadingText}>AI is thinking...</Text>
            </View>
          ) : (
            <Text style={[
              styles.messageText,
              isUser ? styles.userMessageText : styles.aiMessageText
            ]}>
              {message.text}
            </Text>
          )}
        </View>
        <Text style={styles.timestampText}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <StatusBar barStyle="light-content" backgroundColor="#0f0f1a" />
      
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => router.back()}
        >
          <Ionicons name="arrow-back" size={24} color="#5b6cf7" />
        </TouchableOpacity>
        
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>ADHD Chat</Text>
          <View style={styles.statusRow}>
            <View style={[
              styles.statusDot, 
              { backgroundColor: isConnected ? '#10b981' : '#ef4444' }
            ]} />
            <Text style={[
              styles.statusText,
              { color: isConnected ? '#10b981' : '#ef4444' }
            ]}>
              {isConnected ? 'Connected' : 'Offline'}
            </Text>
          </View>
        </View>

        <TouchableOpacity 
          style={styles.clearButton}
          onPress={clearChat}
        >
          <Ionicons name="refresh" size={24} color="#8b5cf6" />
        </TouchableOpacity>
      </View>

      {/* Messages */}
      <ScrollView 
        ref={scrollViewRef}
        style={styles.messagesContainer}
        contentContainerStyle={styles.messagesContent}
        showsVerticalScrollIndicator={false}
      >
        {messages.map(renderMessage)}
      </ScrollView>

      {/* Input Area */}
      <View style={styles.inputContainer}>
        <View style={styles.inputRow}>
          <TextInput
            ref={inputRef}
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder={isConnected ? "Type your message..." : "Connect to start chatting"}
            placeholderTextColor="#94a3b8"
            multiline={true}
            maxLength={1000}
            editable={isConnected && !isLoading}
            onKeyPress={handleKeyPress}
          />
          <TouchableOpacity
            style={[
              styles.sendButton,
              (!inputText.trim() || isLoading || !isConnected) && styles.sendButtonDisabled
            ]}
            onPress={sendMessage}
            disabled={!inputText.trim() || isLoading || !isConnected}
          >
            {isLoading ? (
              <ActivityIndicator size="small" color="white" />
            ) : (
              <Ionicons name="send" size={20} color="white" />
            )}
          </TouchableOpacity>
        </View>
        
        {/* Character count */}
        <Text style={styles.charCount}>
          {inputText.length}/1000
        </Text>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f0f1a', // Deep dark background
  },
  header: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
    backgroundColor: 'rgba(20, 20, 35, 0.95)', // Semi-transparent dark header
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(99, 102, 241, 0.2)', // Subtle purple border
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  backButton: {
    padding: 8,
    borderRadius: 12,
    backgroundColor: 'rgba(91, 108, 247, 0.1)',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 8,
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.4,
    shadowRadius: 3,
  },
  statusText: {
    fontSize: 13,
    fontWeight: '600',
  },
  clearButton: {
    padding: 8,
    borderRadius: 12,
    backgroundColor: 'rgba(139, 92, 246, 0.1)',
  },
  messagesContainer: {
    flex: 1,
    backgroundColor: '#1a1a2e', // Slightly lighter dark background for messages
  },
  messagesContent: {
    padding: 20,
    paddingBottom: 10,
  },
  messageContainer: {
    marginBottom: 20,
  },
  userMessageContainer: {
    alignItems: 'flex-end',
  },
  aiMessageContainer: {
    alignItems: 'flex-start',
  },
  messageContent: {
    maxWidth: '85%',
    borderRadius: 20,
    paddingHorizontal: 18,
    paddingVertical: 14,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 4,
  },
  userMessage: {
    backgroundColor: '#5b6cf7', // Beautiful blue-purple
    shadowColor: '#5b6cf7',
  },
  aiMessage: {
    backgroundColor: 'rgba(31, 31, 50, 0.9)', // Dark semi-transparent
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.2)', // Purple border
    shadowColor: '#8b5cf6',
  },
  messageText: {
    fontSize: 16,
    lineHeight: 24,
    fontWeight: '500',
  },
  userMessageText: {
    color: '#ffffff',
  },
  aiMessageText: {
    color: '#e2e8f0', // Light gray for readability
  },
  timestampText: {
    fontSize: 11,
    color: '#94a3b8', // Muted gray
    marginTop: 6,
    marginHorizontal: 18,
    fontWeight: '500',
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  loadingText: {
    fontSize: 14,
    color: '#a5a5d6',
    fontStyle: 'italic',
    fontWeight: '500',
  },
  inputContainer: {
    padding: 20,
    backgroundColor: 'rgba(20, 20, 35, 0.95)', // Semi-transparent dark
    borderTopWidth: 1,
    borderTopColor: 'rgba(99, 102, 241, 0.2)',
  },
  inputRow: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 12,
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: 'rgba(139, 92, 246, 0.3)', // Purple border
    borderRadius: 24,
    paddingHorizontal: 18,
    paddingVertical: 14,
    fontSize: 16,
    maxHeight: 120,
    backgroundColor: 'rgba(31, 31, 50, 0.8)', // Dark input background
    color: '#ffffff', // White text
    shadowColor: '#8b5cf6',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  sendButton: {
    backgroundColor: '#ff6b9d', // Bright pink accent
    borderRadius: 24,
    width: 48,
    height: 48,
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#ff6b9d',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  sendButtonDisabled: {
    backgroundColor: 'rgba(148, 163, 184, 0.3)', // Muted gray
    shadowOpacity: 0,
  },
  charCount: {
    fontSize: 12,
    color: '#94a3b8', // Muted gray
    textAlign: 'right',
    marginTop: 8,
    fontWeight: '500',
  },
}); 