// Environment configuration
export const ENV = {
  // Backend API URL
  API_URL: __DEV__ 
    ? 'http://localhost:8000'
    : 'https://your-production-url.com',
    
  // Other environment variables
  APP_NAME: 'ADHD Companion',
  VERSION: '1.0.0',
} as const; 