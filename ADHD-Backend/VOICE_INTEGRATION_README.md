# 🎙️ ADHD Companion Voice Integration (Phase 3)

## Overview

The ADHD Companion now includes **real-time voice interaction** using WebSockets and Groq APIs for ultra-fast speech processing optimized for ADHD users.

## 🚀 Features

### Voice-First Design
- **Press-to-Talk**: Simple OpenAI-style interaction (tap to start, tap to stop)
- **Real-time Processing**: WebSocket streaming for instant feedback
- **ADHD-Optimized**: Short responses, clear interruption support

### Groq API Integration
- **Speech-to-Text**: Whisper models with 216x real-time speed
- **Text-to-Speech**: Natural PlayAI voices optimized for clarity
- **Ultra-Low Latency**: Sub-second response times

### WebSocket Voice Flow
```
Frontend → WebSocket → STT (Groq) → AI Processing → TTS (Groq) → Frontend
   ↓           ↓           ↓              ↓             ↓          ↓
  Tap      Audio      Transcribe    Generate      Synthesize   Play
 Circle    Stream      Text         Response      Speech      Audio
```

## 🔧 Setup

### 1. Install Dependencies
```bash
pip install groq
```

### 2. Environment Configuration
Create `.env` file:
```bash
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=sqlite:///./adhd_companion.db
```

Get your Groq API key from: https://console.groq.com/

### 3. Test Installation
```bash
python3 test_voice_integration.py
```

## 📡 WebSocket API

### Connect to Voice Session
```
ws://localhost:8000/ws/voice/{session_id}
```

### Message Types

#### Client → Server
```json
{
  "type": "start_recording"
}

{
  "type": "audio_chunk",
  "data": "base64_encoded_audio"
}

{
  "type": "stop_recording"
}

{
  "type": "interrupt"
}

{
  "type": "set_voice",
  "voice": "calm"
}
```

#### Server → Client
```json
{
  "type": "status",
  "state": "listening|thinking|speaking|idle",
  "message": "Status description"
}

{
  "type": "transcription",
  "text": "What user said",
  "confidence": "high"
}

{
  "type": "ai_response", 
  "text": "AI response text"
}

{
  "type": "audio_chunk",
  "data": "base64_encoded_audio",
  "is_final": false
}

{
  "type": "error",
  "message": "Error description"
}
```

## 🎯 Voice Models

### Speech-to-Text Options
| Model | Speed | Cost/hour | Use Case |
|-------|-------|-----------|----------|
| `whisper-large-v3-turbo` | 216x | $0.04 | Fast multilingual (default) |
| `whisper-large-v3` | 189x | $0.111 | Highest accuracy |
| `distil-whisper-large-v3-en` | 250x | $0.02 | English-only speed |

### Text-to-Speech Voices
- **Calum-PlayAI**: Calm, clear (default for ADHD)
- **Arista-PlayAI**: Professional female
- **Mason-PlayAI**: Friendly male  
- **Celeste-PlayAI**: Warm female
- **Quinn-PlayAI**: Gentle neutral

## 🧠 ADHD Optimizations

### Response Length
- **Target**: Under 50 words per response
- **Maximum**: 200 characters for voice mode
- **Structure**: One clear question or statement

### Speech Optimization
- Removes markdown formatting (`**bold**` → `bold`)
- Converts abbreviations (`etc.` → `and so on`)
- Adds natural pauses with ellipses
- Limits sentence complexity

### Interruption Support
- Users can interrupt AI mid-speech
- Immediate state reset to `idle`
- No penalty for interruptions

### Voice States
1. **idle**: Ready to listen
2. **listening**: Recording user speech
3. **thinking**: Processing STT + AI response
4. **speaking**: Playing AI audio response

## 🏗️ Architecture

### Core Components
- `voice_service.py`: STT/TTS with Groq APIs
- `voice_websocket.py`: WebSocket connection management
- `ai_service.py`: Enhanced with voice conversation support
- `main.py`: WebSocket endpoint integration

### Integration Points
- Existing AI conversation system
- Dynamic timer and planning services
- Session management and user context
- Emotional state detection

## 🔍 Testing

### Run Voice Integration Test
```bash
python3 test_voice_integration.py
```

### Start Development Server
```bash
uvicorn main:app --reload
```

### Test Endpoints
- **API Docs**: http://localhost:8000/docs
- **Voice Models**: http://localhost:8000/api/voice/models
- **Available Voices**: http://localhost:8000/api/voice/voices
- **WebSocket**: ws://localhost:8000/ws/voice/test-session

## 🎯 Next Steps

### Frontend Integration
The frontend already has voice states and WebSocket support. To connect:

1. **WebSocket Connection**:
```typescript
const ws = new WebSocket(`ws://localhost:8000/ws/voice/${sessionId}`);
```

2. **Audio Recording**: Implement microphone capture and base64 encoding
3. **Audio Playback**: Handle incoming audio chunks for TTS playback

### Production Deployment
- Configure Groq API key in production environment
- Set up WebSocket load balancing if needed
- Monitor API usage and costs
- Implement rate limiting for voice requests

---

## 🎉 Success!

Your ADHD Companion now has **voice-first interaction** with:
- ⚡ Ultra-fast speech processing (216x real-time)
- 🧠 ADHD-optimized conversation flow
- 🎙️ Natural voice synthesis
- 📱 WebSocket real-time streaming
- 🔄 Simple press-to-interrupt design

The voice integration maintains all existing dynamic AI conversation capabilities while adding the natural, immediate interaction that ADHD users need! 🚀 