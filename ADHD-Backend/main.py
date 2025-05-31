from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel

# Import our modules
from database import get_db, create_tables, test_connection
from session_service import SessionService
from models import SessionType, SessionStatus, User
from ai_service import ai_service
from timer_service import DynamicTimerService
from chat_service import chat_service

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="ADHD Companion API",
    description="Dynamic AI-powered executive function replacement for ADHD individuals - Text-Based Chat Interface",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8081",  # Expo web development
        "https://*.vercel.app", 
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    user_id: Optional[int] = 1
    text: str

class ChatResponse(BaseModel):
    success: bool
    ai_response: str
    error: Optional[str] = None
    timestamp: Optional[str] = None

class DynamicPlanningRequest(BaseModel):
    user_id: int

class DynamicContinueRequest(BaseModel):
    user_id: int
    user_response: str

class DynamicStateCheckRequest(BaseModel):
    user_id: int
    user_message: str

class WorkBlockStartRequest(BaseModel):
    user_id: int
    task_description: Optional[str] = ""

class WorkBlockConfirmRequest(BaseModel):
    user_id: int
    chosen_duration: int

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
    print("✅ ADHD Companion API v3.0 with Chat Interface is ready!")

@app.get("/")
async def root():
    return {
        "message": "ADHD Companion API v3.0 - Fully Dynamic AI-Driven System with Chat Interface",
        "status": "healthy",
        "version": "3.0.0",
        "features": [
            "Dynamic AI Conversations for All Decisions",
            "Real-time Emotional State Detection", 
            "Fully Adaptive Scheduling (No Hardcoded Values)",
            "Conversational Work Block Creation",
            "Dynamic Break Recommendations",
            "Executive Function Replacement",
            "💬 Text-Based Chat Interface",
            "🤖 Context-Aware AI Conversations"
        ],
        "system_type": "fully_dynamic_llm_driven_with_chat",
        "chat_features": {
            "text_processing": "Real-time AI responses",
            "conversation_history": "Context-aware conversations",
            "adhd_optimized": "Structured responses, clear guidance"
        }
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint with database connectivity"""
    try:
        # Test database query with proper SQLAlchemy usage
        result = db.execute(text("SELECT 1"))
        db.commit()  # Ensure transaction is committed
        
        # Check AI service status
        ai_status = "ready" if ai_service.client is not None else "mock_mode"
        groq_configured = ai_service.client is not None  # Check actual client availability, not just env var
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow(),
            "ai_service": ai_status,
            "groq_configured": groq_configured,
            "system_type": "dynamic_llm_driven",
            "chat_integration": "ready"
        }
    except Exception as e:
        print(f"Health check error: {e}")
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
    request: DynamicPlanningRequest,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Start a completely dynamic planning conversation - NO hardcoded values"""
    try:
        result = await dynamic_service.start_dynamic_planning_conversation(request.user_id)
        
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
    request: DynamicContinueRequest,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Continue the dynamic planning conversation - AI decides what to ask next"""
    try:
        result = await dynamic_service.continue_planning_conversation(request.user_id, request.user_response)
        
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
    request: DynamicStateCheckRequest,
    dynamic_service: DynamicTimerService = Depends(get_dynamic_timer_service)
):
    """Real-time state check using AI conversation - NO hardcoded thresholds"""
    try:
        result = await dynamic_service.dynamic_state_check(request.user_id, request.user_message)
        
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
# CHAT MESSAGING ENDPOINTS
# =====================================

@app.post("/api/chat", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send a chat message and get AI response"""
    try:
        if not request.text.strip():
            return ChatResponse(
                success=False,
                error="Message text is required",
                ai_response="Please provide a message to send."
            )
        
        result = await chat_service.send_chat_message(request.user_id, request.text.strip())
        
        return ChatResponse(
            success=result.get("success", True),
            ai_response=result.get("ai_response", "No response available"),
            error=result.get("error"),
            timestamp=result.get("timestamp")
        )
    except Exception as e:
        return ChatResponse(
            success=False,
            error=str(e),
            ai_response="I'm having trouble processing your message right now. Could you please try again?"
        )

@app.get("/api/chat/history/{user_id}")
async def get_chat_history(user_id: int, limit: int = 50):
    """Get chat history for a user"""
    try:
        history = await chat_service.get_chat_history(user_id, limit)
        return {
            "success": True,
            "user_id": user_id,
            "chat_history": history,
            "total_messages": len(history)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "chat_history": []
        }

@app.delete("/api/chat/history/{user_id}")
async def clear_chat_history(user_id: int):
    """Clear chat history for a user"""
    try:
        success = await chat_service.clear_chat_history(user_id)
        if success:
            return {
                "success": True,
                "message": f"Chat history cleared for user {user_id}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to clear chat history"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Legacy chat endpoint for backward compatibility
@app.post("/chat")
async def legacy_chat(message: dict):
    """Legacy chat endpoint for backward compatibility"""
    try:
        # Use default user ID for legacy endpoint
        DEFAULT_USER_ID = 1
        result = await chat_service.send_chat_message(DEFAULT_USER_ID, message["text"])
        return {"response": result.get("ai_response", "No response available")}
    except Exception as e:
        return {"error": f"Failed to get AI response: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port) 