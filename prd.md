---
title: "ADHD Companion App - Product Requirements Document"
version: "2.0 - Dynamic Adaptive System"
date: "2024"
status: "Draft"
---

# ADHD Companion App - Product Requirements Document

## 🎯 Executive Summary

The ADHD Companion App is an **AI-powered executive function replacement** designed specifically for individuals with ADHD. The app provides **dynamic, real-time adaptive guidance** through AI-initiated sessions that continuously monitor emotional state and adjust throughout the day, acting as a **digital brain scaffold** for missing executive functions.

## 🧠 Problem Statement

Individuals with ADHD struggle with:
- **Executive function deficits** - planning, organization, emotional regulation
- **Two extremes**: Hyperfocus (8+ hours without breaks) OR complete task avoidance
- **Real-time emotional regulation** during work periods
- **Dynamic adaptation** to changing mental states throughout the day
- **Missing internal "controller"** that neurotypical brains provide automatically

## 🎯 Product Vision

Create an **AI digital brain** that dynamically replaces missing executive functions, providing real-time emotional monitoring, adaptive scheduling, and intelligent intervention to maintain healthy balance for ADHD minds.

## 👥 Target Users

**Primary**: Adults with ADHD (18-45 years old)
- Experiencing executive function challenges
- Struggling with hyperfocus or task avoidance extremes
- Need external scaffolding for self-regulation
- Comfortable with AI-powered applications that act as cognitive support

## ✨ Core Features - Dynamic Adaptive System

### 🧠 AI Digital Brain - Executive Function 

#### Core Philosophy:
**The AI acts as the user's external executive function center, providing:**
- Real-time emotional state monitoring
- Dynamic schedule adaptation
- Intelligent intervention timing
- Hyperfocus prevention
- Emotional regulation support
- Task prioritization assistance

### 🌅 Morning Intelligence Analysis

**Dynamic Day Planning Process:**
1. **Morning Conversation Analysis**: AI analyzes user's:
   - Energy level (high/medium/low)
   - Emotional state (stressed/motivated/overwhelmed)
   - Task complexity and count
   - Stress indicators and deadlines
   - Hyperfocus risk assessment

2. **Personalized Schedule Creation**: Based on analysis, AI creates:
   - Custom work block lengths (25/35/45 minutes)
   - Adaptive break timing (10/15/20 minutes)
   - Maximum work blocks before mandatory rest
   - Intervention sensitivity levels
   - Burnout prevention triggers

3. **Real-time Adaptation**: Schedule changes based on:
   - Current emotional state
   - Work progress
   - Detected overwhelm or hyperfocus
   - Energy depletion patterns

### 🔄 Real-Time Emotional State Detection

#### Continuous Monitoring:
- **Language Pattern Analysis**: Detects frustration, overwhelm, exhaustion
- **Behavioral Indicators**: Task avoidance, hyperfocus resistance, distraction
- **Intervention Triggers**: Automatic response to emotional state changes
- **Adaptive Responses**: Changes conversation style based on detected state

#### Emotional States Tracked:
- 😤 **Frustrated**: "This is stupid", "I can't do this"
- 😵 **Overwhelmed**: "Too much", scattered thoughts
- 😴 **Exhausted**: "Brain fog", "Can't focus"
- 🎯 **Hyperfocusing**: Resistance to breaks, "just five more minutes"
- 😑 **Avoidance**: Procrastination language, task switching
- ⚡ **Energized**: High motivation, ready to tackle tasks

### 🎙️ Voice-First Interface

#### Intervention Levels:
1. **Gentle**: Subtle guidance, encouragement
2. **Immediate**: Direct redirection, schedule modification
3. **Emergency**: Full stop, mandatory rest, emotional support

#### Intervention Examples:
- **Hyperfocus Detection** → Force break even if user resists
- **Overwhelm Detection** → Reduce block length, simplify tasks
- **Exhaustion Detection** → End work day, recovery focus
- **Avoidance Detection** → Micro-tasks, motivation building

#### Advanced AI Mode:
- **Hands-free interaction** with pulsing visual feedback
- **Speech-to-Text (STT)** for user input
- **Text-to-Speech (TTS)** for AI responses
- **Real-time conversation** with LLM backend

#### Dynamic Schedule Components:
- **Morning Analysis** → Custom day plan creation
- **Real-time Monitoring** → Continuous emotional state tracking
- **Adaptive Modification** → Schedule changes based on current state
- **Intelligent Pacing** → Prevents both hyperfocus and avoidance

#### Schedule Adaptation Examples:
```
User starts energized → 45-minute blocks planned
↓ (2 hours later)
User shows overwhelm → Blocks reduced to 25 minutes
↓ (1 hour later)  
User shows exhaustion → Work day ends early
```

## 📱 User Interface Design - Voice-First Adaptive

### Screen 1: Adaptive Dashboard
```
┌─────────────────────────┐
│   ADHD Companion        │
├─────────────────────────┤
│                         │
│   [Active Session]      │
│   ┌─────────────────┐   │
│   │  Start Session  │   │
│   │   (Available)   │   │
│   └─────────────────┘   │
│                         │
│        OR               │
│                         │
│   [Timer Mode]          │
│   ┌─────────────────┐   │
│   │ Next Session In │   │
│   │    25:30        │   │
│   └─────────────────┘   │
│                         │
│   ┌─────────────────┐   │
│   │ Talk to AI Now  │   │
│   │   (Override)    │   │
│   └─────────────────┘   │
└─────────────────────────┘
```

### Screen 2: Advanced AI Mode
```
┌─────────────────────────┐
│      AI Voice Mode      │
├─────────────────────────┤
│                         │
│        ┌─────┐          │
│        │  O  │          │
│        │ /|\ │ Pulsing  │
│        │ / \ │ Circle   │
│        └─────┘          │
│                         │
│   Status: Listening     │
│   Status: Thinking      │
│   Status: Speaking      │
│                         │
│   [Chat History]        │
│   ┌─────────────────┐   │
│   │ User: ...       │   │
│   │ AI: ...         │   │
│   └─────────────────┘   │
└─────────────────────────┘
```

## 🔄 Dynamic User Flow

### Adaptive Daily Flow:
```
8:00 AM  → Morning Intelligence Analysis
         ↓ AI analyzes: energy, tasks, emotions
8:15 AM  → Custom Schedule Created
         ↓ Personalized based on analysis
8:30 AM  → Work Block 1 (AI-determined length)
         ↓ Real-time emotional monitoring
9:15 AM  → Emotional State Detection
         ↓ AI detects frustration
9:16 AM  → Immediate Adaptation
         ↓ "Let's try a different approach"
9:20 AM  → Modified Break (longer due to frustration)
         ↓ Schedule automatically adjusted
10:00 AM → Hyperfocus Risk Assessment
         ↓ User wanting to "keep going"
10:01 AM → Mandatory Break Enforcement
         ↓ "I know you want to continue, but..."
```

### Real-Time Adaptation Examples:

**Scenario 1: Hyperfocus Prevention**
```
User: "Just 10 more minutes, I'm almost done!"
AI Detection: Hyperfocus resistance pattern
AI Response: "I can see you're in the zone, but ADHD brains need this break. Trust me on this one. Your work will be better after a reset."
Action: Forces break, extends break time
```

**Scenario 2: Overwhelm Intervention**
```
User: "I don't know where to start, everything feels impossible"
AI Detection: Overwhelm emotional state
AI Response: "That overwhelm feeling is your ADHD brain getting flooded. Let's just pick ONE tiny piece to start with. What's the smallest thing you could do right now?"
Action: Reduces scope, simplifies next task
```
## 🛠️ Technical Architecture

### Backend (FastAPI)
```
┌─────────────────────────────┐
│         FastAPI Backend     │
├─────────────────────────────┤
│ • Session Management API    │
│ • LLM Integration (Groq)    │
│ • Timer/Scheduling Logic    │
│ • User Data Persistence    │
│ • WebSocket/Push Notifications │
└─────────────────────────────┘
```

### Frontend (Expo/React Native)
```
┌─────────────────────────────┐
│      Expo Mobile App        │
├─────────────────────────────┤
│ • Session Dashboard Screen  │
│ • AI Voice Mode Screen      │
│ • Speech-to-Text/TTS       │
│ • Real-time Timer UI       │
│ • Push Notification Handler │
└─────────────────────────────┘
```
## 🛠️ Technical Architecture - Adaptive System

### Backend (FastAPI) - AI Brain Components
```
┌─────────────────────────────┐
│      Adaptive AI Brain      │
├─────────────────────────────┤
│ • Morning Analysis Engine   │
│ • Real-time State Detection │
│ • Dynamic Schedule Creator  │
│ • Intervention Logic        │
│ • Emotional Pattern Learning│
│ • Adaptive Response Generator│
└─────────────────────────────┘
```

### AI Workflow - Dynamic Adaptation
```
User Input → STT → LLM Processing → Session Logic → TTS → User Output

Morning Chat → Analysis → Custom Schedule → Real-time Monitoring → State Detection → Intervention → Schedule Adaptation → Learning
     ↑                                                                                                                    ↓
     └──────────────────────────────── Continuous Feedback Loop ──────────────────────────────────────────────────────┘
```

## 📊 Success Metrics - Executive Function Improvement

### Executive Function Metrics:
- **Emotional regulation improvement**: Fewer overwhelm episodes
- **Hyperfocus prevention**: Successful break enforcement
- **Task completion balance**: Neither avoidance nor hyperfocus extremes
- **Adaptive accuracy**: How well AI predicts user needs
- **Intervention success**: User acceptance of AI guidance

### Dynamic System Metrics:
- **Schedule adaptation frequency**: How often AI modifies plans
- **Emotional state detection accuracy**: Correct identification of user states
- **Intervention timing success**: Right moment for guidance
- **User trust in AI decisions**: Acceptance of AI recommendations
- **Executive function dependency**: User reliance on AI scaffolding

## 🚀 MVP Roadmap - Adaptive System

### ✅ **COMPLETED**
Backend Core 
- [x] Database Models - Enhanced models for sessions, users, emotional states, and adaptations
- [x] AI Integration - Enhanced LLM logic for different session types with adaptive capabilities
- [x] **Session Management** - CRUD operations for the 5 session types
- [x] **Database Configuration** - Set up the enhanced database models
- [x] **Timer & Scheduling Logic** - Implement the dynamic scheduling system
Frontend Foundation
- [x] Session Dashboard screen
- [x] Timer countdown UI
- [x] Basic AI chat interface

### 🔄 **Phase 1: Backend Core (Current Priority)**
- [ ] **API Endpoints** - Connect the adaptive AI to the frontend

### 📱 **Phase 2: Frontend Foundation**
- [ ] API integration

### 🎙️ **Phase 3: Voice Integration**
- [ ] Speech-to-Text implementation
- [ ] Text-to-Speech integration
- [ ] Voice mode UI with pulsing feedback
- [ ] Real-time conversation flow

### ✨ **Phase 4: Polish & Testing**
- [ ] UI/UX refinements
- [ ] Error handling and edge cases
- [ ] Performance optimization
- [ ] User testing and feedback

## 🔒 Technical Requirements

### Backend Dependencies:
```python
# Core Framework
fastapi
uvicorn

# AI & LLM
openai  # For Groq integration
python-dotenv

# Database and State Management
sqlalchemy
alembic
psycopg2-binary

# Real-time Communication
websockets

# Background Tasks and Monitoring
celery
redis
```

### Database Models - Adaptive System:
- **MorningAnalysis**: Store daily analysis results
- **EmotionalState**: Track real-time emotional changes
- **ScheduleAdaptation**: Log all schedule modifications
- **Intervention**: Record all AI interventions
- **UserPattern**: Learn long-term behavioral patterns

## 🎨 Design Principles - Executive Function Support

### ADHD Executive Function Design:
- **Proactive Guidance**: AI initiates, user doesn't have to remember
- **Real-time Adaptation**: Changes based on current state, not fixed rules
- **Emotional Validation**: Acknowledges ADHD struggles without judgment
- **Intelligent Persistence**: Knows when to push and when to back off
- **Scaffolding Philosophy**: Provides structure without feeling controlling

### Dynamic Response Patterns:
- **High Energy**: Longer blocks, more challenging tasks
- **Low Energy**: Shorter blocks, simpler tasks, more encouragement
- **Overwhelm**: Break tasks down, extend breaks, emotional support
- **Hyperfocus**: Firm boundary enforcement, health prioritization
- **Avoidance**: Gentle engagement, micro-tasks, motivation building

## 🔄 Future Enhancements - Advanced Executive Function

### Advanced AI Features:
- **Predictive Emotional Modeling**: Anticipate overwhelm before it happens
- **Biometric Integration**: Heart rate/stress level monitoring
- **Voice Emotion Detection**: Analyze vocal patterns for emotional state
- **Long-term Pattern Learning**: Improve predictions based on historical data
- **Contextual Awareness**: Consider external factors (weather, deadlines, etc.)



## 📋 Acceptance Criteria - Dynamic System

### MVP Success Criteria:
1. **AI accurately analyzes morning conversations** and creates personalized schedules
2. **Real-time emotional state detection** identifies frustration, overwhelm, hyperfocus
3. **Dynamic schedule adaptation** modifies plans based on current user state
4. **Intervention system** successfully guides users through difficult moments
5. **Hyperfocus prevention** enforces breaks even when users resist
6. **Executive function scaffolding** provides structure without feeling controlling
7. **User trusts AI decisions** and accepts adaptive guidance

---
**Development Focus**: Dynamic AI Executive Function Replacement
**Core Innovation**: Real-time adaptive scheduling and emotional regulation
**Target Outcome**: Digital brain that replaces missing ADHD executive functions
**Success Measure**: Balanced productivity without burnout or avoidance extremes

## 📞 Contact & Resources

**Development Team**: Solo Developer (Learning-Focused)
**Timeline**: 5-week MVP development
**Technology Stack**: FastAPI + Expo + Groq LLM
**Target Launch**: MVP for personal use, feedback gathering

**Current Focus**: Phase 1 Backend Core - Session Management, Timer Logic, Database Setup, API Endpoints
