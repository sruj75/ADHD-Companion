# 🧪 ADHD Companion - Test Suite

This directory contains comprehensive tests for the ADHD Companion API system.

## 📁 **Test Files**

### `test_dynamic_system.py` ⭐ **Main System Test**
- **Purpose**: Tests the fully dynamic LLM-driven scheduling system
- **Features Tested**:
  - ✅ Dynamic planning conversations (no hardcoded values)
  - ✅ AI-generated work block duration options
  - ✅ Real-time emotional state analysis
  - ✅ Conversational break decisions
  - ✅ Dynamic schedule adaptations
- **Run Command**: `python3 test_dynamic_system.py`

### `test_session_management.py`
- **Purpose**: Tests the session management system
- **Features Tested**:
  - ✅ Session CRUD operations
  - ✅ Morning analysis processing
  - ✅ Emotional state tracking
  - ✅ Real-time message handling
- **Run Command**: `python3 test_session_management.py`

### `test_timer_scheduling.py` ⚠️ **Legacy Test**
- **Purpose**: Tests for the old static timer system (deprecated)
- **Status**: Kept for reference, but system has been replaced with dynamic version
- **Note**: This tests hardcoded timer logic that is no longer used

## 🚀 **Running Tests**

### From the Test Directory:
```bash
cd Test
python3 test_dynamic_system.py        # Main dynamic system test
python3 test_session_management.py    # Session management test
```

### From the Backend Root:
```bash
python3 Test/test_dynamic_system.py
python3 Test/test_session_management.py
```

## 🎯 **Key Test Scenarios**

### **Dynamic System Test Flow**
1. **Planning Conversation**: AI asks about user state → User responds → AI suggests options
2. **Work Block Creation**: AI analyzes context → Suggests durations → User chooses
3. **Real-time Adaptation**: User sends message → AI analyzes emotional state → Suggests changes
4. **Break Decisions**: Work block ends → AI asks how it went → Suggests break options

### **Session Management Test Flow**
1. **Session Creation**: Create different session types for user
2. **Real-time Messaging**: Send messages during active sessions
3. **Emotional Analysis**: AI detects emotional states from user messages
4. **Schedule Modifications**: System adapts based on user state

## 📊 **Expected Test Results**

✅ **All systems operational**  
✅ **Dynamic conversations working**  
✅ **No hardcoded values used**  
✅ **Real-time adaptation functional**  
✅ **Database operations successful**  

## 🔧 **Test Dependencies**

- SQLite database (auto-created)
- Groq API access (for AI functionality)
- All backend modules properly imported

## 🧠 **Learning from Tests**

These tests demonstrate:
- **LLM-driven decision making** vs traditional if-else logic
- **Conversational interfaces** for user interaction
- **Real-time adaptation** based on natural language
- **Executive function replacement** through AI conversation 