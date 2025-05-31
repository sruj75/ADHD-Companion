from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

# This creates our base class that all database models will inherit from
Base = declarative_base()

class SessionType(str, Enum):
    """
    Enum for the 5 session types mentioned in your PRD.
    Using an Enum ensures we only use valid session types.
    """
    MORNING_PLANNING = "morning_planning"
    POST_WORK_CHECKIN = "post_work_checkin"
    TRANSITION = "transition"
    BURNOUT_PREVENTION = "burnout_prevention"
    EVENING_REFLECTION = "evening_reflection"

class SessionStatus(str, Enum):
    """
    Tracks the current state of a session
    """
    SCHEDULED = "scheduled"  # AI has scheduled this session
    ACTIVE = "active"        # User is currently in this session
    COMPLETED = "completed"  # Session finished successfully
    SKIPPED = "skipped"      # User skipped this session
    ADAPTED = "adapted"      # Session was modified due to emotional state

class EmotionalState(str, Enum):
    """
    Real-time emotional states the AI can detect
    """
    ENERGIZED = "energized"
    FOCUSED = "focused"
    NEUTRAL = "neutral"
    DISTRACTED = "distracted"
    FRUSTRATED = "frustrated"
    OVERWHELMED = "overwhelmed"
    EXHAUSTED = "exhausted"
    HYPERFOCUSING = "hyperfocusing"
    AVOIDANCE = "avoidance"

class InterventionLevel(str, Enum):
    """
    Different levels of AI intervention needed
    """
    NONE = "none"
    GENTLE = "gentle"
    IMMEDIATE = "immediate"
    EMERGENCY = "emergency"

class ScheduleAdaptationType(str, Enum):
    """
    Types of schedule modifications the AI can make
    """
    BLOCK_LENGTH_CHANGE = "block_length_change"
    FORCED_BREAK = "forced_break"
    END_DAY_EARLY = "end_day_early"
    EXTEND_BREAK = "extend_break"
    SIMPLIFY_TASK = "simplify_task"

class User(Base):
    """
    User model - stores basic user information and adaptive preferences
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Dynamic ADHD-specific preferences (learned by AI)
    preferred_work_block_duration = Column(Integer, default=45)  # minutes
    preferred_break_duration = Column(Integer, default=15)       # minutes
    daily_work_limit = Column(Integer, default=240)             # minutes (4 hours)
    intervention_sensitivity = Column(String, default="medium")  # low/medium/high
    
    # Learned patterns (updated by AI)
    typical_energy_pattern = Column(JSON)  # Store time-of-day energy levels
    hyperfocus_triggers = Column(JSON)     # What triggers hyperfocus episodes
    overwhelm_patterns = Column(JSON)      # What causes overwhelm
    
    # Relationships - this creates connections between users and their data
    sessions = relationship("Session", back_populates="user")
    work_blocks = relationship("WorkBlock", back_populates="user")
    morning_analyses = relationship("MorningAnalysis", back_populates="user")
    emotional_states = relationship("EmotionalStateLog", back_populates="user")
    schedule_adaptations = relationship("ScheduleAdaptation", back_populates="user")
    interventions = relationship("InterventionLog", back_populates="user")

class MorningAnalysis(Base):
    """
    Stores the AI's analysis of each morning planning conversation.
    This is the foundation for dynamic schedule creation.
    """
    __tablename__ = "morning_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    analysis_date = Column(DateTime, default=datetime.utcnow)
    
    # Analyzed user state from morning conversation
    emotional_state = Column(String)      # EmotionalState enum value
    energy_level = Column(String)         # high/medium/low
    stress_level = Column(String)         # none/mild/moderate/high
    motivation_level = Column(String)     # low/medium/high
    
    # Task analysis
    task_count = Column(Integer)          # Number of tasks mentioned
    task_complexity = Column(String)      # simple/medium/complex
    estimated_total_time = Column(Integer) # Total estimated work time in minutes
    
    # Risk assessments
    hyperfocus_risk = Column(String)      # low/medium/high
    overwhelm_risk = Column(String)       # low/medium/high
    burnout_risk = Column(String)         # low/medium/high
    
    # AI recommendations based on analysis
    recommended_block_length = Column(Integer)     # minutes
    recommended_break_length = Column(Integer)     # minutes
    max_work_blocks = Column(Integer)              # before mandatory rest
    intervention_sensitivity = Column(String)      # how quickly to intervene
    
    # Store the full conversation for later learning
    conversation_history = Column(JSON)
    
    # Generated schedule based on this analysis
    generated_schedule = Column(JSON)  # List of scheduled activities
    
    # Relationship
    user = relationship("User", back_populates="morning_analyses")

class EmotionalStateLog(Base):
    """
    Real-time tracking of user's emotional state during sessions.
    This enables dynamic adaptation throughout the day.
    """
    __tablename__ = "emotional_state_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=True)
    
    # Timestamp and detection info
    detected_at = Column(DateTime, default=datetime.utcnow)
    emotional_state = Column(String)      # EmotionalState enum value
    confidence_score = Column(Float)      # How confident the AI is (0.0-1.0)
    
    # What triggered this detection
    trigger_message = Column(Text)        # User's message that triggered detection
    context = Column(JSON)               # Additional context (current task, time worked, etc.)
    
    # AI's assessment
    intervention_recommended = Column(String)  # InterventionLevel enum value
    intervention_reason = Column(Text)         # Why this intervention level
    
    # What happened as a result
    action_taken = Column(String)         # What the AI did in response
    user_response = Column(String)        # How user responded to intervention
    
    # Relationships
    user = relationship("User", back_populates="emotional_states")
    session = relationship("Session", back_populates="emotional_states")

class ScheduleAdaptation(Base):
    """
    Logs all modifications made to the user's schedule.
    This tracks how the AI adapts in real-time.
    """
    __tablename__ = "schedule_adaptations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    emotional_state_id = Column(Integer, ForeignKey("emotional_state_logs.id"))
    
    # When and why the adaptation happened
    adapted_at = Column(DateTime, default=datetime.utcnow)
    adaptation_type = Column(String)      # ScheduleAdaptationType enum value
    trigger_reason = Column(Text)         # Why the adaptation was made
    
    # Original vs modified schedule
    original_schedule = Column(JSON)      # What was planned
    modified_schedule = Column(JSON)      # What it was changed to
    
    # Specific changes made
    original_block_length = Column(Integer, nullable=True)
    new_block_length = Column(Integer, nullable=True)
    original_break_length = Column(Integer, nullable=True)
    new_break_length = Column(Integer, nullable=True)
    
    # Impact assessment
    user_acceptance = Column(Boolean, nullable=True)  # Did user accept the change?
    effectiveness_rating = Column(Integer, nullable=True)  # 1-5 scale, filled later
    
    # Relationships
    user = relationship("User", back_populates="schedule_adaptations")
    trigger_state = relationship("EmotionalStateLog")

class InterventionLog(Base):
    """
    Records all AI interventions and their outcomes.
    This helps the AI learn what works for each user.
    """
    __tablename__ = "intervention_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    emotional_state_id = Column(Integer, ForeignKey("emotional_state_logs.id"))
    
    # Intervention details
    intervention_at = Column(DateTime, default=datetime.utcnow)
    intervention_level = Column(String)   # InterventionLevel enum value
    intervention_type = Column(String)    # What kind of intervention
    
    # What the AI did
    ai_message = Column(Text)            # What the AI said to the user
    ai_action = Column(String)           # Any actions taken (schedule change, etc.)
    intervention_strategy = Column(String)  # The approach used (encouraging, firm, etc.)
    
    # User's response
    user_message = Column(Text, nullable=True)     # How user responded
    user_compliance = Column(Boolean, nullable=True)  # Did they follow the guidance?
    user_emotional_response = Column(String, nullable=True)  # Better/worse/same
    
    # Outcome assessment
    intervention_successful = Column(Boolean, nullable=True)  # Did it help?
    follow_up_needed = Column(Boolean, default=False)        # Need more intervention?
    notes = Column(Text, nullable=True)                      # Additional observations
    
    # Relationships
    user = relationship("User", back_populates="interventions")
    trigger_state = relationship("EmotionalStateLog")

class Session(Base):
    """
    Enhanced session model - now includes dynamic adaptation tracking
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Session details
    session_type = Column(String)  # SessionType enum value
    status = Column(String, default=SessionStatus.SCHEDULED)
    
    # Timing information
    scheduled_time = Column(DateTime)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    originally_planned_duration = Column(Integer)  # Original plan in minutes
    actual_duration = Column(Integer, nullable=True)  # How long it actually took
    
    # Adaptation tracking
    was_adapted = Column(Boolean, default=False)     # Was this session modified?
    adaptation_reason = Column(Text, nullable=True)  # Why it was modified
    original_schedule_time = Column(DateTime, nullable=True)  # When it was originally planned
    
    # Session content
    ai_prompt = Column(Text)        # What the AI said to the user
    user_input = Column(Text)       # What the user said back
    session_summary = Column(Text)  # AI-generated summary of the session
    conversation_history = Column(JSON)  # Full conversation for analysis
    
    # Outcome tracking
    session_effectiveness = Column(Integer, nullable=True)  # 1-5 user rating
    emotional_outcome = Column(String, nullable=True)       # How user felt after
    goals_achieved = Column(Boolean, nullable=True)         # Did session meet its goals?
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    emotional_states = relationship("EmotionalStateLog", back_populates="session")

class WorkBlock(Base):
    """
    Enhanced work block model - now tracks dynamic adaptations
    """
    __tablename__ = "work_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Timing
    planned_duration = Column(Integer)  # Original planned minutes
    actual_duration = Column(Integer, nullable=True)  # Actual minutes worked
    started_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    
    # Adaptation tracking
    was_adapted = Column(Boolean, default=False)      # Was duration changed mid-block?
    original_planned_duration = Column(Integer)       # Original plan before any changes
    adaptation_count = Column(Integer, default=0)     # How many times it was modified
    
    # Task information
    task_description = Column(Text)
    task_complexity = Column(String)                  # simple/medium/complex
    completed = Column(Boolean, default=False)
    completion_percentage = Column(Integer, default=0)  # 0-100%
    
    # User state during this block
    starting_energy_level = Column(String, nullable=True)    # high/medium/low
    ending_energy_level = Column(String, nullable=True)      # high/medium/low
    hyperfocus_occurred = Column(Boolean, default=False)     # Did user hyperfocus?
    interruptions_count = Column(Integer, default=0)         # External interruptions
    
    # Block effectiveness
    productivity_rating = Column(Integer, nullable=True)     # 1-5 user rating
    focus_quality = Column(String, nullable=True)            # poor/fair/good/excellent
    
    # Relationships
    user = relationship("User", back_populates="work_blocks")

class UserPattern(Base):
    """
    Stores learned patterns about user behavior for predictive adaptation.
    This is how the AI gets smarter over time.
    """
    __tablename__ = "user_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Pattern identification
    pattern_type = Column(String)         # energy_pattern, overwhelm_trigger, etc.
    pattern_name = Column(String)         # Human-readable pattern name
    detected_at = Column(DateTime, default=datetime.utcnow)
    
    # Pattern details
    pattern_data = Column(JSON)           # The actual pattern data
    confidence_score = Column(Float)      # How confident we are in this pattern
    frequency = Column(Integer)           # How often this pattern occurs
    
    # Pattern triggers
    triggers = Column(JSON)               # What conditions trigger this pattern
    time_of_day_correlation = Column(JSON)  # Time-based patterns
    task_type_correlation = Column(JSON)    # Task-related patterns
    
    # Intervention strategies that work for this pattern
    effective_interventions = Column(JSON)  # What works when this pattern occurs
    ineffective_interventions = Column(JSON)  # What doesn't work
    
    # Learning tracking
    last_updated = Column(DateTime, default=datetime.utcnow)
    accuracy_rate = Column(Float)         # How accurate predictions based on this pattern are
    
    # Relationship
    user = relationship("User") 