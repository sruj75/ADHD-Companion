from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
from datetime import datetime

# Import our modules
from database import get_db, create_tables, test_connection
from session_service import SessionService
from models import SessionType, SessionStatus, User
from ai_service import ai_service
from timer_service import DynamicTimerService
from voice_websocket import voice_websocket_manager

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="ADHD Companion API",
    description="Dynamic AI-powered executive function replacement for ADHD individuals - Now with Voice Integration",
    version="3.0.0"
)

# Add CORS middleware
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

@app.on_event("startup")
async def startup_event():
    """Initialize database and check connections on startup"""
    print("🚀 Starting ADHD Companion API...")
    
    # Test database connection
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Create tables if they don't exist
    create_tables()
    print("✅ ADHD Companion API v3.0 with Voice Integration is ready!")

@app.get("/")
async def root():
    return {
        "message": "ADHD Companion API v3.0 - Fully Dynamic AI-Driven System with Voice Integration",
        "status": "healthy",
        "version": "3.0.0",
        "groq_configured": bool(os.environ.get("GROQ_API_KEY")),
        "features": [
            "Dynamic AI Conversations for All Decisions",
            "Real-time Emotional State Detection", 
            "Fully Adaptive Scheduling (No Hardcoded Values)",
            "Conversational Work Block Creation",
            "Dynamic Break Recommendations",
            "Executive Function Replacement",
            "🎙️ Voice-First Interface with WebSocket STT/TTS",
            "🗣️ Real-time Speech Processing with Groq APIs"
        ],
        "system_type": "fully_dynamic_llm_driven_with_voice",
        "voice_features": {
            "speech_to_text": "Groq Whisper (ultra-fast)",
            "text_to_speech": "Groq PlayAI (natural voices)",
            "real_time": "WebSocket streaming",
            "adhd_optimized": "Short responses, interruption support"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity"""
    try:
        # Test database query
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow(),
            "ai_service": "ready",
            "system_type": "dynamic_llm_driven"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

# Initialize Dynamic Timer Service
def get_dynamic_timer_service():
    db = next(get_db())
    return DynamicTimerService(db)

# =====================================
# SESSION MANAGEMENT ENDPOINTS
# =====================================

@app.post("/api/sessions/create")
async def create_session(
    user_id: int,
    session_type: SessionType,
    scheduled_time: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Creates a new AI session for a user"""
    try:
        session_service = SessionService(db)
        session = session_service.create_session(
            user_id=user_id,
            session_type=session_type,
            scheduled_time=scheduled_time
        )
        
        return {
            "session_id": session.id,
            "session_type": session.session_type,
            "status": session.status,
            "scheduled_time": session.scheduled_time,
            "ai_starter_message": session.ai_prompt,
            "estimated_duration": session.originally_planned_duration
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create session: {str(e)}"
        )

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get details of a specific session"""
    session_service = SessionService(db)
    session = session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    
    return {
        "session_id": session.id,
        "user_id": session.user_id,
        "session_type": session.session_type,
        "status": session.status,
        "scheduled_time": session.scheduled_time,
        "started_at": session.started_at,
        "completed_at": session.completed_at,
        "duration_planned": session.originally_planned_duration,
        "duration_actual": session.actual_duration,
        "conversation_history": session.conversation_history,
        "effectiveness_rating": session.session_effectiveness
    }

@app.post("/api/sessions/{session_id}/start")
async def start_session(session_id: int, db: Session = Depends(get_db)):
    """Start a scheduled session"""
    try:
        session_service = SessionService(db)
        session = session_service.start_session(session_id)
        
        return {
            "session_id": session.id,
            "status": session.status,
            "started_at": session.started_at,
            "ai_starter_message": session.ai_prompt,
            "message": "Session started successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@app.post("/api/sessions/{session_id}/complete")
async def complete_session(
    session_id: int,
    user_input: str = "",
    session_summary: str = "",
    effectiveness_rating: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Complete an active session"""
    try:
        session_service = SessionService(db)
        session = session_service.complete_session(
            session_id=session_id,
            user_input=user_input,
            session_summary=session_summary,
            effectiveness_rating=effectiveness_rating
        )
        
        return {
            "session_id": session.id,
            "status": session.status,
            "completed_at": session.completed_at,
            "actual_duration": session.actual_duration,
            "effectiveness_rating": session.session_effectiveness,
            "message": "Session completed successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@app.post("/api/sessions/{session_id}/message")
async def send_message(
    session_id: int,
    user_message: str,
    db: Session = Depends(get_db)
):
    """Send a message during an active session with real-time adaptation"""
    try:
        session_service = SessionService(db)
        session = session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        if session.status != SessionStatus.ACTIVE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Session {session_id} is not active"
            )
        
        # Get current conversation history
        conversation_history = session.conversation_history or []
        
        # Process the message with real-time adaptation
        result = await session_service.handle_real_time_message(
            session_id=session_id,
            user_message=user_message,
            conversation_history=conversation_history
        )
        
        return {
            "session_id": session_id,
            "ai_response": result["ai_response"],
            "emotional_state_detected": result["emotional_state"],
            "intervention_level": result["intervention_level"],
            "schedule_modifications": result["modifications_needed"],
            "conversation_updated": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )

# =====================================
# DYNAMIC AI-DRIVEN TIMER ENDPOINTS
# =====================================

@app.post("/api/dynamic/planning/start")
async def start_dynamic_planning(
    user_id: int,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Start a completely dynamic planning conversation - NO hardcoded values"""
    try:
        result = await dynamic_service.start_dynamic_planning_conversation(user_id)
        
        return {
            "success": result["success"],
            "message": "Dynamic planning conversation started",
            "ai_question": result.get("ai_question"),
            "conversation_id": result.get("conversation_id"),
            "system_type": "fully_dynamic_llm_driven"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/dynamic/planning/continue")
async def continue_dynamic_planning(
    user_id: int,
    user_response: str,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Continue the dynamic planning conversation - AI decides what to ask next"""
    try:
        result = await dynamic_service.continue_planning_conversation(user_id, user_response)
        
        return {
            "success": result["success"],
            "ai_response": result.get("ai_response"),
            "conversation_state": result.get("conversation_state"),
            "message": "Conversation continued dynamically"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/dynamic/work-block/start")
async def start_dynamic_work_block(
    user_id: int,
    task_description: str = "",
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Start work block with AI-determined duration options - NO hardcoded durations"""
    try:
        result = await dynamic_service.start_dynamic_work_block(user_id, task_description)
        
        return {
            "success": result["success"],
            "ai_question": result.get("ai_question"),
            "duration_options": result.get("duration_options"),
            "reasoning": result.get("reasoning"),
            "awaiting_user_choice": result.get("awaiting_user_choice", False),
            "message": "Dynamic work block options presented"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/dynamic/work-block/confirm")
async def confirm_dynamic_duration(
    user_id: int,
    chosen_duration: int,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Confirm user's chosen work block duration and start timer"""
    try:
        result = await dynamic_service.confirm_work_block_duration(user_id, chosen_duration)
        
        return {
            "success": result["success"],
            "work_block_id": result.get("work_block_id"),
            "duration": result.get("duration"),
            "start_time": result.get("start_time"),
            "message": result.get("message"),
            "system_type": "user_chosen_dynamic_duration"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/dynamic/state-check")
async def dynamic_state_check(
    user_id: int,
    user_message: str,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Real-time state check using AI conversation - NO hardcoded thresholds"""
    try:
        result = await dynamic_service.dynamic_state_check(user_id, user_message)
        
        return {
            "success": result["success"],
            "adaptation_response": result.get("adaptation_response"),
            "current_work_context": result.get("current_work_context"),
            "message": "Dynamic state analysis completed"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/dynamic/break/decide")
async def decide_dynamic_break(
    user_id: int,
    work_block_id: int,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """AI-driven break decision - NO predetermined break lengths"""
    try:
        result = await dynamic_service.dynamic_break_decision(user_id, work_block_id)
        
        return {
            "success": result["success"],
            "check_in_question": result.get("check_in_question"),
            "break_options": result.get("break_options"),
            "option_descriptions": result.get("option_descriptions"),
            "reasoning": result.get("reasoning"),
            "message": "Dynamic break options suggested"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/dynamic/status/{user_id}")
async def get_dynamic_status(
    user_id: int,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Get current dynamic system status including active conversations"""
    try:
        status = await dynamic_service.get_dynamic_status(user_id)
        
        return {
            "success": True,
            "status": status,
            "message": "Dynamic status retrieved"
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# =====================================
# USER & ANALYTICS ENDPOINTS
# =====================================

@app.get("/api/users/{user_id}/sessions")
async def get_user_sessions(
    user_id: int,
    status: Optional[SessionStatus] = None,
    session_type: Optional[SessionType] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Get sessions for a user with optional filtering"""
    session_service = SessionService(db)
    sessions = session_service.get_user_sessions(
        user_id=user_id,
        status=status,
        session_type=session_type,
        limit=limit
    )
    
    return {
        "user_id": user_id,
        "sessions": [
            {
                "session_id": s.id,
                "session_type": s.session_type,
                "status": s.status,
                "scheduled_time": s.scheduled_time,
                "completed_at": s.completed_at,
                "effectiveness_rating": s.session_effectiveness
            }
            for s in sessions
        ],
        "total_count": len(sessions)
    }

@app.get("/api/users/{user_id}/statistics")
async def get_user_statistics(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get session statistics and insights for a user"""
    session_service = SessionService(db)
    stats = session_service.get_session_statistics(user_id, days)
    
    return {
        "user_id": user_id,
        "period_days": days,
        "statistics": stats,
        "insights": {
            "most_common_session_type": max(stats["session_type_breakdown"], key=stats["session_type_breakdown"].get) if stats["session_type_breakdown"] else None,
            "completion_trend": "good" if stats["completion_rate"] > 70 else "needs_improvement",
            "effectiveness_trend": "high" if stats["average_effectiveness"] > 3.5 else "moderate"
        }
    }

@app.get("/api/users/{user_id}/emotional-patterns")
async def get_emotional_patterns(
    user_id: int,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get recent emotional state patterns for a user"""
    session_service = SessionService(db)
    emotional_states = session_service.get_recent_emotional_states(user_id, hours)
    
    # Analyze patterns
    state_counts = {}
    for state in emotional_states:
        state_counts[state.emotional_state] = state_counts.get(state.emotional_state, 0) + 1
    
    return {
        "user_id": user_id,
        "period_hours": hours,
        "emotional_states": [
            {
                "detected_at": state.detected_at,
                "emotional_state": state.emotional_state,
                "confidence_score": state.confidence_score,
                "intervention_recommended": state.intervention_recommended
            }
            for state in emotional_states
        ],
        "patterns": {
            "state_frequency": state_counts,
            "most_common_state": max(state_counts, key=state_counts.get) if state_counts else None,
            "intervention_needed_count": len([s for s in emotional_states if s.intervention_recommended != "none"])
        }
    }

# =====================================
# LEGACY CHAT ENDPOINT
# =====================================

@app.post("/chat")
async def legacy_chat(message: dict):
    """Legacy chat endpoint for backward compatibility"""
    try:
        response = await ai_service.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": message["text"]}],
            temperature=0.7
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"error": f"Failed to get AI response: {str(e)}"}

# =====================================
# 🎙️ VOICE WEBSOCKET ENDPOINT
# =====================================

@app.websocket("/ws/voice/{session_id}")
async def voice_websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time voice interactions
    
    Supports:
    - Real-time audio streaming (STT)
    - AI conversation processing  
    - Speech synthesis streaming (TTS)
    - Voice state management (listening/thinking/speaking)
    - Interruption handling
    """
    await voice_websocket_manager.connect(websocket, session_id)
    await voice_websocket_manager.handle_voice_session(websocket, session_id)

# =====================================
# REST API VOICE ENDPOINTS
# =====================================

@app.get("/api/voice/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    from voice_service import voice_service
    
    return {
        "available_voices": voice_service.get_available_voices(),
        "default_voice": voice_service.default_voice,
        "voice_recommendations": {
            "calm": "Calum-PlayAI",
            "professional": "Arista-PlayAI",
            "friendly": "Mason-PlayAI", 
            "warm": "Celeste-PlayAI",
            "confident": "Atlas-PlayAI",
            "gentle": "Quinn-PlayAI"
        }
    }

@app.get("/api/voice/models") 
async def get_voice_models():
    """Get available STT and TTS models"""
    return {
        "stt_models": {
            "whisper-large-v3-turbo": {
                "description": "Fastest multilingual model",
                "cost_per_hour": "$0.04",
                "real_time_factor": "216x",
                "languages": "multilingual"
            },
            "whisper-large-v3": {
                "description": "Highest accuracy multilingual",
                "cost_per_hour": "$0.111", 
                "real_time_factor": "189x",
                "languages": "multilingual"
            },
            "distil-whisper-large-v3-en": {
                "description": "Fastest English-only",
                "cost_per_hour": "$0.02",
                "real_time_factor": "250x", 
                "languages": "english_only"
            }
        },
        "tts_models": {
            "playai-tts": {
                "description": "Natural English voices",
                "voices": 19,
                "languages": ["english"]
            },
            "playai-tts-arabic": {
                "description": "Arabic voices",
                "voices": 4,
                "languages": ["arabic"]
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port) 