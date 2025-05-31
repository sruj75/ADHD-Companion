#!/usr/bin/env python3
"""
Dynamic Conversational Timer Service for ADHD Companion

This service uses LLM conversations to make ALL scheduling decisions in real-time:
- No hardcoded work block durations
- No predetermined break lengths  
- No fixed intervention thresholds
- Everything is determined through AI conversation with the user

The LLM acts as a dynamic decision-maker that asks questions and adapts based on responses.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models import (
    WorkBlock, 
    Session as SessionModel,
    User,
    MorningAnalysis,
    EmotionalStateLog,
    ScheduleAdaptation
)
from session_service import SessionService, SessionType

class ConversationalState(str, Enum):
    """Current state of dynamic conversation"""
    INITIAL_PLANNING = "initial_planning"
    WORK_BLOCK_DECISION = "work_block_decision"
    BREAK_DECISION = "break_decision"
    ADAPTATION_CONVERSATION = "adaptation_conversation"
    INTERVENTION_DIALOGUE = "intervention_dialogue"
    CONTINUATION_CHECK = "continuation_check"

class DynamicTimerService:
    """
    Fully dynamic timer service that uses LLM conversations for ALL decisions
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.session_service = SessionService(db)
        self.active_conversations: Dict[int, Dict] = {}  # user_id -> conversation state
        self.active_timers: Dict[int, Dict] = {}  # work_block_id -> timer info
        
        # Import AI service here to avoid circular imports
        from ai_service import ai_service
        self.ai_service = ai_service
    
    # =====================================
    # DYNAMIC SCHEDULE CREATION THROUGH CONVERSATION
    # =====================================
    
    async def start_dynamic_planning_conversation(self, user_id: int) -> Dict:
        """
        Start a completely dynamic planning conversation.
        NO preset values - everything determined through AI dialogue.
        """
        
        # Get user's recent patterns for context (but don't use as defaults)
        user_context = await self._get_user_context(user_id)
        
        # Start completely open-ended conversation
        initial_prompt = f"""
        You are an ADHD executive function replacement assistant. Start a natural conversation to understand this user's current state and plan their day dynamically.

        User Context (for reference only, don't assume): {user_context}

        Your job is to:
        1. Ask how they're feeling RIGHT NOW
        2. Understand their energy and focus level TODAY
        3. Find out what they want to accomplish
        4. Determine optimal work block duration through conversation
        5. Decide break lengths based on their responses
        6. Create a personalized schedule through dialogue

        Start with a natural question about how they're feeling today. Be conversational, not clinical.
        Don't mention any specific time durations yet - let their responses guide you.
        """
        
        try:
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[{"role": "system", "content": initial_prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            ai_question = response.choices[0].message.content
            
            # Initialize conversation state
            self.active_conversations[user_id] = {
                "state": ConversationalState.INITIAL_PLANNING,
                "conversation_history": [
                    {"role": "assistant", "content": ai_question}
                ],
                "gathered_info": {},
                "schedule_decisions": {},
                "started_at": datetime.utcnow()
            }
            
            return {
                "success": True,
                "ai_question": ai_question,
                "conversation_id": user_id,
                "next_action": "await_user_response"
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to start conversation: {e}"}
    
    async def continue_planning_conversation(self, user_id: int, user_response: str) -> Dict:
        """
        Continue the dynamic planning conversation based on user response.
        The AI decides what to ask next and when enough info is gathered.
        """
        
        if user_id not in self.active_conversations:
            return {"success": False, "error": "No active conversation found"}
        
        conversation = self.active_conversations[user_id]
        conversation["conversation_history"].append({"role": "user", "content": user_response})
        
        # Build dynamic prompt based on conversation state
        conversation_context = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in conversation["conversation_history"]
        ])
        
        dynamic_prompt = f"""
        Continue this ADHD planning conversation. Based on the user's latest response, decide what to do next:

        Conversation so far:
        {conversation_context}

        Current conversation state: {conversation["state"].value}
        Information gathered so far: {conversation["gathered_info"]}

        Your options:
        1. If you need more info about their current state - ask another question
        2. If you have enough info about how they're feeling - suggest specific work block duration options
        3. If they've agreed on work duration - ask about break preferences  
        4. If you have all needed info - create their personalized schedule

        Guidelines:
        - Ask specific questions: "Would you prefer 20, 30, or 45 minutes for your first work block?"
        - Let THEM choose durations based on how they feel
        - Adapt suggestions based on their energy/stress level
        - If they seem overwhelmed, suggest shorter blocks
        - If they're energized, offer longer options
        - Always give them 2-3 specific choices

        Respond with either:
        - Another question to gather more info
        - OR specific time options for them to choose from  
        - OR a complete schedule if you have all needed information

        Format your response as JSON:
        {{
            "type": "question|options|schedule", 
            "content": "your response text",
            "needs_user_input": true|false,
            "suggested_durations": [20, 30, 45] (if offering options),
            "schedule": {{...}} (if complete)
        }}
        """
        
        try:
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[{"role": "user", "content": dynamic_prompt}],
                temperature=0.6,
                max_tokens=300
            )
            
            ai_response_text = response.choices[0].message.content
            conversation["conversation_history"].append({"role": "assistant", "content": ai_response_text})
            
            # Try to parse JSON response
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
                if json_match:
                    ai_response = json.loads(json_match.group())
                else:
                    # Fallback if no JSON found
                    ai_response = {
                        "type": "question",
                        "content": ai_response_text,
                        "needs_user_input": True
                    }
            except:
                ai_response = {
                    "type": "question", 
                    "content": ai_response_text,
                    "needs_user_input": True
                }
            
            # Update conversation state based on AI response
            if ai_response["type"] == "schedule":
                conversation["state"] = ConversationalState.WORK_BLOCK_DECISION
                # Create the actual schedule
                schedule = await self._create_schedule_from_conversation(user_id, ai_response.get("schedule", {}))
                ai_response["schedule"] = schedule
            
            return {
                "success": True,
                "ai_response": ai_response,
                "conversation_state": conversation["state"].value
            }
            
        except Exception as e:
            return {"success": False, "error": f"Conversation error: {e}"}
    
    # =====================================
    # DYNAMIC WORK BLOCK CREATION
    # =====================================
    
    async def start_dynamic_work_block(self, user_id: int, task_description: str = "") -> Dict:
        """
        Start a work block using completely dynamic duration determination.
        Ask the user in real-time how long they want to work.
        """
        
        # Get current user context
        user_context = await self._get_user_context(user_id)
        recent_performance = await self._get_recent_performance(user_id)
        
        # Ask AI to determine best duration options based on current state
        duration_prompt = f"""
        A user with ADHD wants to start a work block. Based on their context, what duration options should we offer them?

        User context: {user_context}
        Recent performance: {recent_performance}
        Task description: {task_description}
        Current time: {datetime.utcnow().strftime('%H:%M')}

        Provide 3 specific duration options that make sense for their current state and ask them to choose.
        Consider:
        - Their energy level
        - Time of day
        - Recent work patterns
        - Task complexity

        Respond with JSON:
        {{
            "question": "conversational question to ask user",
            "duration_options": [15, 25, 35],
            "reasoning": "why these durations make sense"
        }}
        """
        
        try:
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[{"role": "user", "content": duration_prompt}],
                temperature=0.6,
                max_tokens=250
            )
            
            ai_response_text = response.choices[0].message.content
            
            # Parse AI response
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
                if json_match:
                    ai_response = json.loads(json_match.group())
                else:
                    # Fallback
                    ai_response = {
                        "question": "How long would you like to work? Would you prefer 20, 30, or 40 minutes?",
                        "duration_options": [20, 30, 40],
                        "reasoning": "Offering flexible options based on your preferences"
                    }
            except:
                ai_response = {
                    "question": "How long would you like to work right now? I can suggest 15, 25, or 35 minutes based on how you're feeling.",
                    "duration_options": [15, 25, 35],
                    "reasoning": "Adaptive options for current state"
                }
            
            # Store pending work block info
            self.active_conversations[user_id] = {
                "state": ConversationalState.WORK_BLOCK_DECISION,
                "pending_work_block": {
                    "task_description": task_description,
                    "duration_options": ai_response["duration_options"]
                },
                "conversation_history": [
                    {"role": "assistant", "content": ai_response["question"]}
                ]
            }
            
            return {
                "success": True,
                "ai_question": ai_response["question"],
                "duration_options": ai_response["duration_options"],
                "reasoning": ai_response["reasoning"],
                "awaiting_user_choice": True
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to create dynamic work block: {e}"}
    
    async def confirm_work_block_duration(self, user_id: int, chosen_duration: int) -> Dict:
        """
        User has chosen their work block duration. Start the timer.
        """
        
        if user_id not in self.active_conversations:
            return {"success": False, "error": "No pending work block decision"}
        
        conversation = self.active_conversations[user_id]
        pending_block = conversation.get("pending_work_block", {})
        
        # Create work block with user-chosen duration
        work_block = WorkBlock(
            user_id=user_id,
            planned_duration=chosen_duration,
            started_at=datetime.utcnow(),
            task_description=pending_block.get("task_description", ""),
            completed=False,
            interruptions_count=0,
            hyperfocus_occurred=False
        )
        
        self.db.add(work_block)
        self.db.commit()
        self.db.refresh(work_block)
        
        # Start timer
        timer_info = {
            "work_block": work_block,
            "start_time": datetime.utcnow(),
            "chosen_duration": chosen_duration,
            "state": "running",
            "pause_count": 0
        }
        
        self.active_timers[work_block.id] = timer_info
        
        # Clear conversation state
        del self.active_conversations[user_id]
        
        return {
            "success": True,
            "work_block_id": work_block.id,
            "duration": chosen_duration,
            "start_time": work_block.started_at,
            "message": f"Started {chosen_duration}-minute work block. I'll check in with you dynamically!"
        }
    
    # =====================================
    # DYNAMIC REAL-TIME ADAPTATION
    # =====================================
    
    async def dynamic_state_check(self, user_id: int, user_message: str) -> Dict:
        """
        Real-time check-in that uses AI to determine if any adaptations are needed.
        NO hardcoded thresholds - everything through conversation.
        """
        
        # Get current work context
        active_work_blocks = [
            timer for work_block_id, timer in self.active_timers.items()
            if timer["work_block"].user_id == user_id and timer["state"] == "running"
        ]
        
        current_work_context = {}
        if active_work_blocks:
            timer = active_work_blocks[0]
            elapsed = (datetime.utcnow() - timer["start_time"]).total_seconds() / 60
            current_work_context = {
                "work_block_id": timer["work_block"].id,
                "planned_duration": timer["chosen_duration"],
                "elapsed_minutes": int(elapsed),
                "remaining_minutes": timer["chosen_duration"] - int(elapsed),
                "task_description": timer["work_block"].task_description
            }
        
        # Ask AI to analyze the user's message and current state
        adaptation_prompt = f"""
        A user with ADHD just sent this message during their work session: "{user_message}"

        Current work context: {current_work_context}
        Time of day: {datetime.utcnow().strftime('%H:%M')}

        Analyze their message for:
        1. How they're feeling right now
        2. Whether they need any support or changes
        3. If their current work block should be modified
        4. What kind of response would be most helpful

        Based on their message, determine if any adaptations are needed and respond conversationally.

        Respond with JSON:
        {{
            "emotional_state_detected": "frustrated|overwhelmed|focused|energized|tired|distracted",
            "needs_adaptation": true|false,
            "suggested_action": "continue|pause|shorten_block|take_break|end_early|change_approach",
            "ai_response": "conversational response to user",
            "reasoning": "why this adaptation is suggested"
        }}

        Be natural and supportive in your response. Ask follow-up questions if needed.
        """
        
        try:
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[{"role": "user", "content": adaptation_prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            ai_response_text = response.choices[0].message.content
            
            # Parse AI response
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
                if json_match:
                    adaptation_response = json.loads(json_match.group())
                else:
                    # Fallback parsing
                    adaptation_response = {
                        "emotional_state_detected": "neutral",
                        "needs_adaptation": False,
                        "suggested_action": "continue",
                        "ai_response": ai_response_text,
                        "reasoning": "Continuing with current approach"
                    }
            except:
                adaptation_response = {
                    "emotional_state_detected": "neutral", 
                    "needs_adaptation": False,
                    "suggested_action": "continue",
                    "ai_response": "I'm here to help! How are you feeling about your current work?",
                    "reasoning": "Standard supportive response"
                }
            
            # Execute any needed adaptations
            if adaptation_response["needs_adaptation"] and current_work_context:
                await self._execute_dynamic_adaptation(
                    work_block_id=current_work_context["work_block_id"],
                    suggested_action=adaptation_response["suggested_action"],
                    reasoning=adaptation_response["reasoning"]
                )
            
            return {
                "success": True,
                "adaptation_response": adaptation_response,
                "current_work_context": current_work_context
            }
            
        except Exception as e:
            return {"success": False, "error": f"Dynamic check failed: {e}"}
    
    async def dynamic_break_decision(self, user_id: int, work_block_id: int) -> Dict:
        """
        When a work block ends, use AI conversation to determine break duration.
        NO predetermined break lengths.
        """
        
        # Get work block performance data
        timer_info = self.active_timers.get(work_block_id, {})
        work_block = timer_info.get("work_block")
        
        if not work_block:
            return {"success": False, "error": "Work block not found"}
        
        elapsed_time = (datetime.utcnow() - timer_info["start_time"]).total_seconds() / 60
        
        # Ask AI to suggest break options based on how the work block went
        break_prompt = f"""
        A user with ADHD just finished a work block. Help determine their optimal break duration through conversation.

        Work block details:
        - Planned duration: {timer_info['chosen_duration']} minutes
        - Actual duration: {int(elapsed_time)} minutes
        - Task: {work_block.task_description}
        - Time of day: {datetime.utcnow().strftime('%H:%M')}

        Ask them how the work block went and suggest 2-3 specific break duration options that make sense.
        
        Consider:
        - How they might be feeling after this work session
        - What kind of break would be most restorative
        - Time of day and energy patterns

        Respond with JSON:
        {{
            "check_in_question": "How did that work block go? How are you feeling?",
            "break_options": [5, 15, 25],
            "option_descriptions": ["Quick breather", "Standard break", "Longer rest"],
            "reasoning": "why these options make sense"
        }}
        """
        
        try:
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.model,
                messages=[{"role": "user", "content": break_prompt}],
                temperature=0.6,
                max_tokens=250
            )
            
            ai_response_text = response.choices[0].message.content
            
            # Parse response
            try:
                import json
                import re
                json_match = re.search(r'\{.*\}', ai_response_text, re.DOTALL)
                if json_match:
                    break_response = json.loads(json_match.group())
                else:
                    break_response = {
                        "check_in_question": "How did that work session go? What kind of break feels right?",
                        "break_options": [10, 20, 30],
                        "option_descriptions": ["Quick break", "Standard break", "Longer break"],
                        "reasoning": "Flexible break options"
                    }
            except:
                break_response = {
                    "check_in_question": "How are you feeling after that work block?",
                    "break_options": [10, 15, 20],
                    "option_descriptions": ["Quick", "Medium", "Long"],
                    "reasoning": "Standard options"
                }
            
            # Update conversation state for break decision
            self.active_conversations[user_id] = {
                "state": ConversationalState.BREAK_DECISION,
                "completed_work_block_id": work_block_id,
                "break_options": break_response["break_options"],
                "conversation_history": [
                    {"role": "assistant", "content": break_response["check_in_question"]}
                ]
            }
            
            return {
                "success": True,
                "check_in_question": break_response["check_in_question"],
                "break_options": break_response["break_options"],
                "option_descriptions": break_response["option_descriptions"],
                "reasoning": break_response["reasoning"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Break decision failed: {e}"}
    
    # =====================================
    # HELPER METHODS
    # =====================================
    
    async def _get_user_context(self, user_id: int) -> Dict:
        """Get current user context for AI decision making"""
        
        # Get recent emotional states
        recent_states = self.session_service.get_recent_emotional_states(user_id, hours=24)
        
        # Get recent work blocks
        recent_work = self.db.query(WorkBlock).filter(
            and_(
                WorkBlock.user_id == user_id,
                WorkBlock.started_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).order_by(WorkBlock.started_at.desc()).limit(10).all()
        
        return {
            "recent_emotional_states": [
                {"state": s.emotional_state, "time": s.detected_at} 
                for s in recent_states[-5:]  # Last 5 states
            ],
            "recent_work_patterns": [
                {
                    "duration": wb.actual_duration or wb.planned_duration,
                    "completion": wb.completion_percentage,
                    "focus_quality": wb.focus_quality
                }
                for wb in recent_work
            ],
            "time_of_day": datetime.utcnow().strftime('%H:%M'),
            "day_of_week": datetime.utcnow().strftime('%A')
        }
    
    async def _get_recent_performance(self, user_id: int) -> Dict:
        """Get recent performance metrics"""
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_work = self.db.query(WorkBlock).filter(
            and_(
                WorkBlock.user_id == user_id,
                WorkBlock.started_at >= today_start
            )
        ).all()
        
        if not today_work:
            return {"message": "No work completed today yet"}
        
        total_time = sum(wb.actual_duration or 0 for wb in today_work)
        avg_completion = sum(wb.completion_percentage or 0 for wb in today_work) / len(today_work)
        
        return {
            "time_worked_today": total_time,
            "work_blocks_completed": len(today_work),
            "average_completion_rate": avg_completion,
            "last_break_time": max(wb.completed_at for wb in today_work if wb.completed_at) if today_work else None
        }
    
    async def _execute_dynamic_adaptation(self, work_block_id: int, suggested_action: str, reasoning: str):
        """Execute adaptations suggested by AI"""
        
        if work_block_id not in self.active_timers:
            return
        
        timer_info = self.active_timers[work_block_id]
        
        if suggested_action == "pause":
            timer_info["state"] = "paused"
            timer_info["pause_count"] += 1
            
        elif suggested_action == "shorten_block":
            # Reduce remaining time
            elapsed = (datetime.utcnow() - timer_info["start_time"]).total_seconds() / 60
            new_duration = int(elapsed) + 10  # Give 10 more minutes
            timer_info["chosen_duration"] = new_duration
            
        elif suggested_action == "end_early":
            timer_info["state"] = "completed_early"
            await self._complete_work_block_early(work_block_id, reasoning)
    
    async def _complete_work_block_early(self, work_block_id: int, reason: str):
        """Complete a work block early due to AI suggestion"""
        
        timer_info = self.active_timers[work_block_id]
        work_block = timer_info["work_block"]
        
        work_block.completed_at = datetime.utcnow()
        work_block.actual_duration = int((datetime.utcnow() - timer_info["start_time"]).total_seconds() / 60)
        work_block.completed = True
        work_block.completion_percentage = 75  # Assume reasonable completion for early end
        
        self.db.commit()
        
        # Remove from active timers
        del self.active_timers[work_block_id]
    
    async def _create_schedule_from_conversation(self, user_id: int, schedule_data: Dict) -> List[Dict]:
        """Create actual schedule from conversation results"""
        
        # This would create a full schedule based on the conversation
        # For now, return a simple structure
        return [{
            "type": "dynamic_schedule",
            "created_from": "ai_conversation",
            "user_id": user_id,
            "schedule_data": schedule_data,
            "created_at": datetime.utcnow()
        }]
    
    # =====================================
    # STATUS AND MONITORING
    # =====================================
    
    async def get_dynamic_status(self, user_id: int) -> Dict:
        """Get current dynamic status including any active conversations"""
        
        active_conversation = self.active_conversations.get(user_id)
        active_work_blocks = [
            {
                "work_block_id": work_block_id,
                "state": timer["state"],
                "elapsed_minutes": int((datetime.utcnow() - timer["start_time"]).total_seconds() / 60),
                "remaining_minutes": timer["chosen_duration"] - int((datetime.utcnow() - timer["start_time"]).total_seconds() / 60),
                "task": timer["work_block"].task_description
            }
            for work_block_id, timer in self.active_timers.items()
            if timer["work_block"].user_id == user_id
        ]
        
        return {
            "user_id": user_id,
            "has_active_conversation": active_conversation is not None,
            "conversation_state": active_conversation["state"].value if active_conversation else None,
            "active_work_blocks": active_work_blocks,
            "system_type": "fully_dynamic_ai_driven",
            "last_update": datetime.utcnow()
        } 