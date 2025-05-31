from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import (
    Session as SessionModel, 
    User, 
    SessionType, 
    SessionStatus,
    MorningAnalysis,
    EmotionalStateLog,
    ScheduleAdaptation,
    InterventionLog
)
from ai_service import ai_service, EmotionalState

class SessionService:
    """
    Comprehensive service for managing AI-guided sessions.
    Handles CRUD operations, session lifecycle, and integration with adaptive AI.
    """
    
    def __init__(self, db: Session):
        self.db = db
        
    # =====================================
    # CREATE OPERATIONS
    # =====================================
    
    def create_session(
        self, 
        user_id: int, 
        session_type: SessionType,
        scheduled_time: Optional[datetime] = None
    ) -> SessionModel:
        """
        Creates a new AI session.
        
        Args:
            user_id: ID of the user
            session_type: Type of session (morning_planning, post_work_checkin, etc.)
            scheduled_time: When the session should happen (defaults to now)
        
        Returns:
            Created session object
        """
        if scheduled_time is None:
            scheduled_time = datetime.utcnow()
            
        # Get the appropriate AI starter message for this session type
        starter_message = ai_service.get_session_starter(session_type)
        
        session = SessionModel(
            user_id=user_id,
            session_type=session_type.value,
            status=SessionStatus.SCHEDULED.value,
            scheduled_time=scheduled_time,
            originally_planned_duration=ai_service.get_recommended_session_timing(session_type),
            ai_prompt=starter_message,
            conversation_history=[]
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        print(f"✅ Created {session_type} session for user {user_id}")
        return session
    
    def create_morning_analysis(
        self, 
        user_id: int, 
        conversation_history: List[Dict],
        analysis_data: Dict
    ) -> MorningAnalysis:
        """
        Creates a morning analysis record based on the morning planning conversation.
        This drives the dynamic schedule creation.
        """
        analysis = MorningAnalysis(
            user_id=user_id,
            analysis_date=datetime.utcnow(),
            emotional_state=analysis_data.get("emotional_state"),
            energy_level=analysis_data.get("energy_level"),
            stress_level=analysis_data.get("stress_indicators"),
            motivation_level=analysis_data.get("motivation_level", "medium"),
            task_count=analysis_data.get("task_count", 3),
            task_complexity=analysis_data.get("task_complexity"),
            hyperfocus_risk=analysis_data.get("hyperfocus_risk"),
            overwhelm_risk=analysis_data.get("overwhelm_risk", "medium"),
            burnout_risk=analysis_data.get("burnout_risk", "medium"),
            recommended_block_length=analysis_data.get("recommended_block_length"),
            recommended_break_length=analysis_data.get("recommended_break_length"),
            max_work_blocks=analysis_data.get("max_work_blocks"),
            intervention_sensitivity=analysis_data.get("intervention_sensitivity"),
            conversation_history=conversation_history,
            generated_schedule=analysis_data.get("generated_schedule", [])
        )
        
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        
        print(f"✅ Created morning analysis for user {user_id}")
        return analysis
    
    def log_emotional_state(
        self,
        user_id: int,
        session_id: Optional[int],
        emotional_state: str,
        trigger_message: str,
        confidence_score: float = 0.8,
        intervention_recommended: str = "none"
    ) -> EmotionalStateLog:
        """
        Logs detected emotional state during a session.
        This enables real-time adaptation.
        """
        state_log = EmotionalStateLog(
            user_id=user_id,
            session_id=session_id,
            detected_at=datetime.utcnow(),
            emotional_state=emotional_state,
            confidence_score=confidence_score,
            trigger_message=trigger_message,
            intervention_recommended=intervention_recommended,
            context={
                "session_type": self.get_session(session_id).session_type if session_id else None,
                "time_of_day": datetime.utcnow().strftime("%H:%M")
            }
        )
        
        self.db.add(state_log)
        self.db.commit()
        self.db.refresh(state_log)
        
        print(f"📊 Logged {emotional_state} state for user {user_id}")
        return state_log
    
    # =====================================
    # READ OPERATIONS
    # =====================================
    
    def get_session(self, session_id: int) -> Optional[SessionModel]:
        """
        Retrieves a session by ID.
        """
        return self.db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    def get_user_sessions(
        self, 
        user_id: int, 
        status: Optional[SessionStatus] = None,
        session_type: Optional[SessionType] = None,
        limit: int = 50
    ) -> List[SessionModel]:
        """
        Gets sessions for a user with optional filtering.
        
        Args:
            user_id: User to get sessions for
            status: Filter by session status (optional)
            session_type: Filter by session type (optional)
            limit: Maximum number of sessions to return
        """
        query = self.db.query(SessionModel).filter(SessionModel.user_id == user_id)
        
        if status:
            query = query.filter(SessionModel.status == status.value)
        if session_type:
            query = query.filter(SessionModel.session_type == session_type.value)
            
        return query.order_by(SessionModel.scheduled_time.desc()).limit(limit).all()
    
    def get_active_session(self, user_id: int) -> Optional[SessionModel]:
        """
        Gets the currently active session for a user.
        """
        return self.db.query(SessionModel).filter(
            and_(
                SessionModel.user_id == user_id,
                SessionModel.status == SessionStatus.ACTIVE.value
            )
        ).first()
    
    def get_next_scheduled_session(self, user_id: int) -> Optional[SessionModel]:
        """
        Gets the next scheduled session for a user.
        """
        return self.db.query(SessionModel).filter(
            and_(
                SessionModel.user_id == user_id,
                SessionModel.status == SessionStatus.SCHEDULED.value,
                SessionModel.scheduled_time > datetime.utcnow()
            )
        ).order_by(SessionModel.scheduled_time.asc()).first()
    
    def get_todays_sessions(self, user_id: int) -> List[SessionModel]:
        """
        Gets all sessions for today for a user.
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return self.db.query(SessionModel).filter(
            and_(
                SessionModel.user_id == user_id,
                SessionModel.scheduled_time >= today_start,
                SessionModel.scheduled_time < today_end
            )
        ).order_by(SessionModel.scheduled_time.asc()).all()
    
    def get_latest_morning_analysis(self, user_id: int) -> Optional[MorningAnalysis]:
        """
        Gets the most recent morning analysis for a user.
        """
        return self.db.query(MorningAnalysis).filter(
            MorningAnalysis.user_id == user_id
        ).order_by(MorningAnalysis.analysis_date.desc()).first()
    
    def get_recent_emotional_states(self, user_id: int, hours: int = 4) -> List[EmotionalStateLog]:
        """
        Gets recent emotional state logs for pattern analysis.
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return self.db.query(EmotionalStateLog).filter(
            and_(
                EmotionalStateLog.user_id == user_id,
                EmotionalStateLog.detected_at >= cutoff_time
            )
        ).order_by(EmotionalStateLog.detected_at.desc()).all()
    
    # =====================================
    # UPDATE OPERATIONS
    # =====================================
    
    def start_session(self, session_id: int) -> SessionModel:
        """
        Marks a session as active and records start time.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = SessionStatus.ACTIVE.value
        session.started_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        
        print(f"▶️ Started session {session_id}")
        return session
    
    def complete_session(
        self, 
        session_id: int, 
        user_input: str = "",
        session_summary: str = "",
        effectiveness_rating: Optional[int] = None
    ) -> SessionModel:
        """
        Marks a session as completed and records outcome data.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = SessionStatus.COMPLETED.value
        session.completed_at = datetime.utcnow()
        session.user_input = user_input
        session.session_summary = session_summary
        session.session_effectiveness = effectiveness_rating
        
        # Calculate actual duration
        if session.started_at:
            duration = session.completed_at - session.started_at
            session.actual_duration = int(duration.total_seconds() / 60)  # Convert to minutes
        
        self.db.commit()
        self.db.refresh(session)
        
        print(f"✅ Completed session {session_id}")
        return session
    
    def skip_session(self, session_id: int, reason: str = "") -> SessionModel:
        """
        Marks a session as skipped.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.status = SessionStatus.SKIPPED.value
        session.completed_at = datetime.utcnow()
        session.session_summary = f"Skipped: {reason}"
        
        self.db.commit()
        self.db.refresh(session)
        
        print(f"⏭️ Skipped session {session_id}")
        return session
    
    def update_session_conversation(
        self, 
        session_id: int, 
        conversation_history: List[Dict]
    ) -> SessionModel:
        """
        Updates the conversation history for a session.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        session.conversation_history = conversation_history
        
        self.db.commit()
        self.db.refresh(session)
        
        return session
    
    # =====================================
    # DELETE OPERATIONS
    # =====================================
    
    def delete_session(self, session_id: int) -> bool:
        """
        Deletes a session. Use with caution - mainly for cleanup.
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        
        print(f"🗑️ Deleted session {session_id}")
        return True
    
    # =====================================
    # BUSINESS LOGIC OPERATIONS
    # =====================================
    
    async def process_morning_planning(
        self, 
        user_id: int, 
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Processes a completed morning planning session.
        Analyzes the conversation and creates a dynamic schedule.
        """
        # Analyze the morning conversation
        analysis_data = await ai_service.analyze_morning_session(conversation_history)
        
        # Create analysis record
        analysis = self.create_morning_analysis(user_id, conversation_history, analysis_data)
        
        # Generate dynamic schedule
        current_time = datetime.utcnow()
        schedule = ai_service.create_dynamic_schedule(analysis_data, current_time)
        
        # Create scheduled sessions based on the analysis
        scheduled_sessions = []
        for scheduled_item in schedule:
            if scheduled_item["type"] in ["post_work_checkin", "transition", "burnout_prevention"]:
                session_type = SessionType(scheduled_item["type"])
                session = self.create_session(
                    user_id=user_id,
                    session_type=session_type,
                    scheduled_time=scheduled_item["start_time"]
                )
                scheduled_sessions.append(session)
        
        return {
            "analysis": analysis,
            "schedule": schedule,
            "scheduled_sessions": scheduled_sessions,
            "recommendations": {
                "block_length": analysis_data.get("recommended_block_length"),
                "break_length": analysis_data.get("recommended_break_length"),
                "max_blocks": analysis_data.get("max_work_blocks"),
                "intervention_sensitivity": analysis_data.get("intervention_sensitivity")
            }
        }
    
    async def handle_real_time_message(
        self,
        session_id: int,
        user_message: str,
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """
        Processes a user message during an active session.
        Detects emotional state and adapts response accordingly.
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Detect emotional state from the message
        emotional_analysis = await ai_service.detect_emotional_state(
            user_message, 
            conversation_history
        )
        
        # Log the emotional state
        emotional_log = self.log_emotional_state(
            user_id=session.user_id,
            session_id=session_id,
            emotional_state=emotional_analysis["emotional_state"],
            trigger_message=user_message,
            intervention_recommended=emotional_analysis.get("intervention_needed", "none")
        )
        
        # Check if schedule modification is needed
        modifications = ai_service.should_modify_schedule(
            emotional_analysis,
            current_block=1,  # Would get this from work block tracking
            time_worked=120   # Would calculate from today's work blocks
        )
        
        # Generate adaptive AI response
        session_context = {
            "session_type": session.session_type,
            "session_id": session_id
        }
        
        day_progress = {
            "time_worked_today": 120,  # Would calculate from work blocks
            "sessions_completed": 2    # Would count from today's sessions
        }
        
        ai_response = await ai_service.generate_adaptive_response(
            user_message=user_message,
            session_context=session_context,
            emotional_state=emotional_analysis,
            day_progress=day_progress
        )
        
        # Update conversation history
        updated_conversation = conversation_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": ai_response}
        ]
        
        self.update_session_conversation(session_id, updated_conversation)
        
        return {
            "ai_response": ai_response,
            "emotional_state": emotional_analysis,
            "modifications_needed": modifications,
            "intervention_level": emotional_analysis.get("intervention_needed", "none")
        }
    
    def get_session_statistics(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Gets session statistics for analytics and insights.
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = self.db.query(SessionModel).filter(
            and_(
                SessionModel.user_id == user_id,
                SessionModel.scheduled_time >= cutoff_date
            )
        ).all()
        
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == SessionStatus.COMPLETED.value])
        skipped_sessions = len([s for s in sessions if s.status == SessionStatus.SKIPPED.value])
        
        # Session type breakdown
        session_type_counts = {}
        for session in sessions:
            session_type_counts[session.session_type] = session_type_counts.get(session.session_type, 0) + 1
        
        # Average effectiveness rating
        effectiveness_ratings = [s.session_effectiveness for s in sessions if s.session_effectiveness]
        avg_effectiveness = sum(effectiveness_ratings) / len(effectiveness_ratings) if effectiveness_ratings else 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "skipped_sessions": skipped_sessions,
            "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            "session_type_breakdown": session_type_counts,
            "average_effectiveness": avg_effectiveness,
            "period_days": days
        } 