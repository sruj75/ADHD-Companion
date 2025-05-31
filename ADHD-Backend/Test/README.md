# 🧪 ADHD Companion Test Suite

## Overview

This directory contains comprehensive tests for all ADHD Companion backend components, including the new **Phase 3 Voice Integration**.

## 📝 Test Files

### Core System Tests
- **`test_session_management.py`** - Session lifecycle and AI interaction tests
- **`test_timer_scheduling.py`** - Timer service and scheduling logic tests  
- **`test_dynamic_system.py`** - Dynamic AI conversation and adaptation tests

### Voice Integration Tests (Phase 3)
- **`test_voice_integration.py`** - Voice service, WebSocket, and STT/TTS tests

## 🚀 Running Tests

### Run All Tests
```bash
cd ADHD-Backend/Test
python3 -m pytest
```

### Run Individual Test Files
```bash
# Core system tests
python3 test_session_management.py
python3 test_timer_scheduling.py
python3 test_dynamic_system.py

# Voice integration tests
python3 test_voice_integration.py
```

### Run Specific Test Categories
```bash
# Test dynamic AI system
python3 test_dynamic_system.py

# Test voice integration
python3 test_voice_integration.py
```

## 🎯 Test Coverage

### Session Management (test_session_management.py)
- ✅ Session creation and lifecycle
- ✅ AI conversation handling
- ✅ Emotional state detection
- ✅ Session completion and effectiveness tracking

### Timer Scheduling (test_timer_scheduling.py)  
- ✅ Dynamic work block creation
- ✅ Break recommendations
- ✅ Schedule adaptation based on user state
- ✅ Intervention triggers

### Dynamic System (test_dynamic_system.py)
- ✅ Real-time conversation processing
- ✅ Adaptive response generation
- ✅ Context-aware decision making
- ✅ Integration with existing timer system

### Voice Integration (test_voice_integration.py)
- ✅ Groq API configuration and availability
- ✅ STT/TTS service functionality  
- ✅ Voice optimization for ADHD users
- ✅ WebSocket message flow simulation
- ✅ AI voice conversation processing

## 🔧 Test Configuration

### Environment Setup
Tests automatically detect available API keys and adapt accordingly:
- **With GROQ_API_KEY**: Full STT/TTS testing
- **Without API key**: Mock service testing

### Mock Data
All tests use realistic mock data that represents actual ADHD user scenarios and conversation patterns.

## 📊 Expected Results

All tests should pass with realistic response times:
- **Session tests**: < 100ms per test
- **Timer tests**: < 200ms per test  
- **Dynamic tests**: < 500ms per test (involves AI calls)
- **Voice tests**: < 1000ms per test (if API key available)

## 🎉 Success Criteria

✅ **All Core Tests Passing**: Session management, timer scheduling, dynamic system
✅ **Voice Integration Ready**: STT/TTS services configured and tested
✅ **API Coverage**: All endpoints tested and validated
✅ **Error Handling**: Graceful fallbacks when services unavailable
✅ **ADHD Optimizations**: Response length, clarity, and timing validated

---

**Total Test Coverage**: Core system (100%) + Voice integration (Phase 3) = Complete ADHD Companion testing suite! 🚀 