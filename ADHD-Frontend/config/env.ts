import Constants from 'expo-constants';
import { Platform } from 'react-native';

// Environment configuration
export const ENV = {
  // Backend API URL - use environment variable or default
  // For web development, use localhost; for mobile, use your computer's IP
  API_URL: Constants.expoConfig?.extra?.apiUrl || (__DEV__ 
    ? Platform.OS === 'web' 
      ? 'http://localhost:8000'  // Web development - use localhost
      : 'http://192.168.0.103:8000'  // Mobile development - use your computer's IP
    : 'https://your-production-url.com'),
    
  // Other environment variables
  APP_NAME: 'ADHD Companion',
  VERSION: '1.0.0',
  
  // User ID for development (replace with auth system later)
  DEV_USER_ID: 1,
  
  // API timeouts
  API_TIMEOUT: 10000,
} as const; 