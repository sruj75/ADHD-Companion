---

## 🚀 Phase 1: Web Deployment (Current)

### Backend: FastAPI → Render

#### Prerequisites:
- GitHub repository with your FastAPI code
- Render account (free tier available)

#### Step-by-Step Backend Deployment:

1. **Prepare Your FastAPI App**
   ```python
   # Ensure your main.py has proper CORS setup
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "https://*.vercel.app",
           "https://your-custom-domain.com"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Create requirements.txt**
   ```bash
   cd ADHD-Backend
   pip freeze > requirements.txt
   ```

3. **Deploy to Render**
   - Go to [render.com](https://render.com)
   - Create new "Web Service"
   - Connect GitHub repository
   - Use these settings:
   
   | Setting | Value |
   |---------|--------|
   | **Language** | Python 3 |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | **Environment** | Add `GROQ_API_KEY` |

4. **Test Backend**
   ```bash
   curl https://your-app.onrender.com/
   # Should return: {"message": "ADHD Companion API is running!"}
   ```

### Frontend: Expo → Vercel

#### Prerequisites:
- Vercel account
- Expo app configured for web

#### Step-by-Step Frontend Deployment:

1. **Test Local Web Build**
   ```bash
   cd ADHD-Frontend
   npm run web
   # Verify app works in browser
   ```

2. **Configure API URL**
   ```typescript
   // config/api.ts
   const API_BASE_URL = process.env.NODE_ENV === 'production' 
     ? 'https://your-app.onrender.com'
     : 'http://localhost:8000';
   
   export { API_BASE_URL };
   ```

3. **Deploy to Vercel**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy from frontend directory
   cd ADHD-Frontend
   vercel
   
   # Follow prompts:
   # - Project name: adhd-companion
   # - Framework: Other
   # - Build command: expo export --platform web
   # - Output directory: dist
   ```

4. **Configure Environment Variables in Vercel**
   - Go to Vercel dashboard
   - Project Settings → Environment Variables
   - Add: `EXPO_PUBLIC_API_URL=https://your-backend.onrender.com`

5. **Test Deployment**
   - Visit: `https://your-app.vercel.app`
   - Test session flow and API connectivity

#### Web Implementation Notes:
- **Voice features**: Uses Web Speech API (browser-dependent, but same voice UI)
- **Notifications**: Browser notifications instead of push (requires user permission)
- **Background timers**: Tab-based timers (same timing logic, different implementation)
- **Performance**: Web rendering vs native (same features, different optimization)

> **Note**: These are technical implementation differences only. The complete ADHD Companion experience - all session types, AI conversations, timers, and user flows - work identically on web and mobile.

---

## 📱 Phase 2: Native Mobile Deployment (Future)

### TestFlight Beta Testing

#### Prerequisites:
- Apple Developer Account ($99/year)
- macOS with Xcode
- EAS Build account

#### Step-by-Step TestFlight Deployment:

1. **Configure EAS Build**
   ```bash
   # Install EAS CLI
   npm install -g @expo/eas-cli
   
   # Login and configure
   cd ADHD-Frontend
   eas login
   eas build:configure
   ```

2. **Update app.json for iOS**
   ```json
   {
     "expo": {
       "name": "ADHD Companion",
       "slug": "adhd-companion",
       "version": "1.0.0",
       "ios": {
         "bundleIdentifier": "com.yourname.adhdcompanion",
         "buildNumber": "1"
       }
     }
   }
   ```

3. **Build for iOS**
   ```bash
   # Build for TestFlight
   eas build --platform ios --profile preview
   
   # This creates an .ipa file
   ```

4. **Submit to TestFlight**
   ```bash
   # Submit to App Store Connect
   eas submit --platform ios
   ```

5. **Invite Beta Testers**
   - Go to App Store Connect
   - TestFlight section
   - Add internal/external testers
   - Send invitation links

### App Store Production

#### Prerequisites:
- Completed TestFlight testing
- App Store Connect setup
- App review compliance

#### Step-by-Step App Store Submission:

1. **Prepare Production Build**
   ```bash
   # Update version in app.json
   # Build production version
   eas build --platform ios --profile production
   ```

2. **App Store Assets**
   - App icons (various sizes)
   - Screenshots (different device sizes)
   - App description and keywords
   - Privacy policy URL

3. **Submit for Review**
   ```bash
   eas submit --platform ios --profile production
   ```

4. **App Review Process**
   - Apple reviews app (1-7 days)
   - Address any feedback
   - App goes live after approval

---

## 🔧 Technical Considerations

### Cross-Platform Feature Planning

#### Core App Features (Same on Web & Mobile):
- ✅ **Complete session management** - All 5 session types work identically
- ✅ **AI-driven conversation flow** - Same LLM integration and session logic
- ✅ **Timer countdown & work blocks** - Full Pomodoro functionality
- ✅ **Proactive session scheduling** - AI initiates sessions exactly as planned
- ✅ **Session dashboard** - Both screens work identically
- ✅ **Voice mode interface** - Same UI, with platform-specific voice implementation
- ✅ **Complete user flow** - Morning → Work → Check-in → Reflection (unchanged)
- ✅ **Burnout prevention** - Same algorithm and timing logic
- ✅ **Emergency AI access** - "Talk to AI Now" button works identically

#### Platform-Specific Implementation Details:
**Web Version:**
- 🎙️ **Voice features**: Uses Web Speech API (browser-dependent)
- 🔔 **Notifications**: Browser notifications (requires permission)
- ⏰ **Background timers**: Web-based timers (tab must remain open)
- 💾 **Data persistence**: Local storage + API calls

**Mobile Version:** 
- 🎙️ **Voice features**: Native expo-speech (more reliable)
- 🔔 **Notifications**: Native push notifications (works when app closed)
- ⏰ **Background timers**: True background processing
- 💾 **Data persistence**: Device storage + API calls

> **Important**: The web version implements the exact same ADHD Companion experience with identical session flows, AI logic, and user interface. The only differences are platform-specific technical implementations, not feature changes.

### Code Structure for Cross-Platform

```typescript
// utils/platform.ts
import { Platform } from 'react-native';

export const isWeb = Platform.OS === 'web';
export const isMobile = Platform.OS !== 'web';

// features/voice/VoiceHandler.ts
export const VoiceHandler = {
  startListening: () => {
    if (isWeb) {
      // Web Speech API fallback
      return startWebSpeechRecognition();
    } else {
      // Native expo-speech
      return startNativeSpeechRecognition();
    }
  }
};
```

---

## 📊 Environment Configuration

### Development vs Production

```bash
# .env.development (local)
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_ENV=development

# .env.production (deployed)
EXPO_PUBLIC_API_URL=https://your-backend.onrender.com
EXPO_PUBLIC_ENV=production
```

### Backend Environment Variables

```bash
# Render environment variables
GROQ_API_KEY=your_groq_api_key
DATABASE_URL=your_database_url
JWT_SECRET=your_jwt_secret
CORS_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

---

## 🚀 Deployment Checklist

### Phase 1: Web Deployment ✅
- [ ] Backend deployed to Render
- [ ] Frontend deployed to Vercel
- [ ] CORS configured properly
- [ ] Environment variables set
- [ ] Basic features working
- [ ] Shareable URL generated
- [ ] Friends can test via web

### Phase 2: Mobile Preparation 🔄
- [ ] Apple Developer Account purchased
- [ ] EAS Build configured
- [ ] Native voice features implemented
- [ ] Push notification setup
- [ ] App icons and assets prepared
- [ ] App Store Connect configured

### Phase 3: TestFlight Beta 📱
- [ ] iOS build successful
- [ ] TestFlight submission complete
- [ ] Beta testers invited
- [ ] Feedback collected and addressed
- [ ] Native features tested thoroughly

### Phase 4: App Store Release 🌟
- [ ] Production build created
- [ ] App Store assets uploaded
- [ ] App review submitted
- [ ] Marketing materials prepared
- [ ] Launch strategy planned

---

## 🎯 Success Metrics

### Web Phase Metrics:
- **User engagement**: Time spent in sessions
- **Feature usage**: Which session types are most used
- **Technical performance**: API response times
- **User feedback**: Ease of use, feature requests

### Mobile Phase Metrics:
- **App Store ratings**: Target 4.5+ stars
- **Retention rate**: Daily/weekly active users
- **Native feature adoption**: Voice mode usage
- **Performance**: App launch time, battery usage

---

## 🔄 Continuous Deployment

### Automated Deployment Pipeline:

```yaml
# GitHub Actions example
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    # Auto-deploy to Render on push
    
  deploy-frontend:
    # Auto-deploy to Vercel on push
    
  build-mobile:
    # Trigger EAS build on version tags
```

---

## 📞 Support & Resources

### Documentation Links:
- [Expo Web Documentation](https://docs.expo.dev/workflow/web/)
- [EAS Build Guide](https://docs.expo.dev/build/introduction/)
- [Render FastAPI Deployment](https://render.com/docs/deploy-fastapi)
- [Vercel Deployment](https://vercel.com/docs)
- [App Store Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)

### Community Resources:
- Expo Discord
- React Native Community
- r/reactnative subreddit

---

**Next Step**: Start with Phase 1 web deployment to get immediate feedback, then gradually move toward native mobile deployment for the full ADHD Companion experience! 🚀
