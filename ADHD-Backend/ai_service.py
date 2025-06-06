from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import re
import json
import openai
import os
from dotenv import load_dotenv

load_dotenv()

class EmotionalState(str, Enum):
    """Real-time emotional states the AI can detect"""
    ENERGIZED = "energized"
    FOCUSED = "focused"
    NEUTRAL = "neutral"
    DISTRACTED = "distracted"
    FRUSTRATED = "frustrated"
    OVERWHELMED = "overwhelmed"
    EXHAUSTED = "exhausted"
    HYPERFOCUSING = "hyperfocusing"

class UserCondition(str, Enum):
    """Overall user condition that affects day planning"""
    HIGH_ENERGY = "high_energy"
    MEDIUM_ENERGY = "medium_energy"  
    LOW_ENERGY = "low_energy"
    STRESSED = "stressed"
    OVERWHELMED = "overwhelmed"
    MOTIVATED = "motivated"

class AdaptiveAIService:
    """
    Dynamic AI that creates personalized schedules and adapts in real-time.
    This is the 'digital brain' that replaces missing executive function.
    """
    
    def __init__(self):
        # Initialize OpenAI client for Groq with simplified configuration
        try:
            # Check if GROQ_API_KEY is available
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if not groq_api_key or groq_api_key == "your_groq_api_key_here":
                print("⚠️ No GROQ_API_KEY found - running in mock mode")
                self.client = None
            else:
                self.client = openai.OpenAI(
                    base_url="https://api.groq.com/openai/v1",
                    api_key=groq_api_key,
                    timeout=30.0
                )
                print("✅ AI service initialized successfully with Groq API")
        except Exception as e:
            print(f"⚠️ AI service initialization warning: {e}")
            print("Running in mock mode - add GROQ_API_KEY to enable AI features")
            self.client = None
        
        self.model = "llama-3.1-8b-instant"
        
    def get_session_starter(self, session_type, user_context: Dict = None) -> str:
        """
        Returns an appropriate opening message for each session type.
        This is what the AI says first when a session begins.
        """
        
        current_time = datetime.now().strftime('%I:%M %p')
        
        if hasattr(session_type, 'value'):
            session_type_str = session_type.value
        else:
            session_type_str = str(session_type)
        
        if session_type_str == "morning_planning":
            return f"Good morning! ☀️ It's {current_time} and time for our morning planning session. How are you feeling today? What's your energy level like?"
        
        elif session_type_str == "post_work_checkin":
            return f"Hey there! 👋 You just finished a work block - how did that go? How are you feeling right now?"
        
        elif session_type_str == "transition":
            return f"Ready to dive back in? 🎯 How are you feeling after your break? Let's get you set up for your next work session."
        
        elif session_type_str == "burnout_prevention":
            return f"Hold up! 🛑 You've been working hard for several hours now. It's time for a mandatory rest period. I know you might want to keep going, but your brain needs this break. How are you feeling right now?"
        
        elif session_type_str == "evening_reflection":
            return f"Time to wind down! 🌙 It's {current_time} and the workday is done. Let's reflect on how today went. What are you most proud of accomplishing today?"
        
        else:
            return "Hi! I'm here to help. What's on your mind?"
    
    def get_recommended_session_timing(self, session_type) -> int:
        """
        Returns recommended session duration in minutes for each type.
        
        These are based on ADHD attention patterns and research.
        """
        
        if hasattr(session_type, 'value'):
            session_type_str = session_type.value
        else:
            session_type_str = str(session_type)
        
        timing_map = {
            "morning_planning": 10,      # Enough time to plan, not too long to delay starting
            "post_work_checkin": 5,      # Quick emotional regulation
            "transition": 3,             # Brief re-engagement
            "burnout_prevention": 15,    # Longer to ensure real rest
            "evening_reflection": 8,     # Meaningful reflection without overthinking
        }
        
        return timing_map.get(session_type_str, 5)  # Default 5 minutes
    
    async def analyze_morning_session(self, conversation_history: List[Dict]) -> Dict:
        """
        Analyzes the morning planning conversation to extract:
        - User's emotional/energy state
        - Number and complexity of tasks
        - Stress level and motivation
        - Recommended day structure
        """
        
        if not self.client:
            # Return default analysis if no AI client
            return self._default_day_plan()
        
        # Combine all user messages from morning session
        user_messages = [msg["content"] for msg in conversation_history if msg["role"] == "user"]
        full_conversation = " ".join(user_messages)
        
        analysis_prompt = f"""
        Analyze this morning planning conversation with someone who has ADHD. Extract:
        
        1. EMOTIONAL_STATE: (energized/focused/neutral/distracted/frustrated/overwhelmed/exhausted)
        2. ENERGY_LEVEL: (high/medium/low) 
        3. TASK_COUNT: How many main tasks they mentioned
        4. TASK_COMPLEXITY: (simple/medium/complex) based on task descriptions
        5. STRESS_INDICATORS: (none/mild/moderate/high) - look for deadline pressure, anxiety
        6. HYPERFOCUS_RISK: (low/medium/high) - big projects, perfectionism, excitement
        7. RECOMMENDED_BLOCK_LENGTH: (25/35/45) minutes based on their state
        8. RECOMMENDED_BREAK_LENGTH: (10/15/20) minutes  
        9. MAX_WORK_BLOCKS: How many blocks before mandatory long break
        10. INTERVENTION_SENSITIVITY: (low/medium/high) - how quickly to intervene if struggling
        
        Conversation: {full_conversation}
        
        Return as JSON format with these exact keys.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Parse the AI's analysis (you'd want more robust JSON parsing here)
            analysis_text = response.choices[0].message.content
            
            # Extract key insights (simplified - you'd want more robust parsing)
            return self._parse_morning_analysis(analysis_text)
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            # Fallback to default moderate settings
            return self._default_day_plan()
    
    def create_dynamic_schedule(self, morning_analysis: Dict, current_time: datetime) -> List[Dict]:
        """
        Creates a personalized schedule based on morning analysis.
        This is where the AI becomes the user's external executive function.
        """
        
        schedule = []
        work_block_length = morning_analysis.get("recommended_block_length", 45)
        break_length = morning_analysis.get("recommended_break_length", 15)
        max_blocks = morning_analysis.get("max_work_blocks", 4)
        
        start_time = current_time
        
        for block_num in range(max_blocks):
            # Work block
            work_end = start_time + timedelta(minutes=work_block_length)
            schedule.append({
                "type": "work_block",
                "start_time": start_time,
                "end_time": work_end,
                "duration_minutes": work_block_length,
                "block_number": block_num + 1
            })
            
            # Check-in session
            checkin_end = work_end + timedelta(minutes=5)
            schedule.append({
                "type": "post_work_checkin", 
                "start_time": work_end,
                "end_time": checkin_end,
                "duration_minutes": 5
            })
            
            # Break (longer break after block 2 or 3)
            break_duration = break_length if block_num < 2 else break_length + 10
            break_end = checkin_end + timedelta(minutes=break_duration)
            schedule.append({
                "type": "break",
                "start_time": checkin_end,
                "end_time": break_end, 
                "duration_minutes": break_duration
            })
            
            start_time = break_end
            
            # Insert burnout prevention after block 3
            if block_num == 2:  # After 3rd block
                burnout_end = start_time + timedelta(minutes=20)
                schedule.append({
                    "type": "burnout_prevention",
                    "start_time": start_time,
                    "end_time": burnout_end,
                    "duration_minutes": 20,
                    "mandatory": True
                })
                start_time = burnout_end
        
        return schedule
    
    async def detect_emotional_state(self, user_message: str, conversation_context: List[Dict]) -> Dict:
        """
        Real-time emotional state detection from user's language.
        This is key for dynamic adaptation.
        """
        
        if not self.client:
            # Return neutral state if no AI client
            return {"emotional_state": "neutral", "intervention_needed": "none"}
        
        detection_prompt = f"""
        Analyze this message from someone with ADHD for emotional/mental state indicators:
        
        Current message: "{user_message}"
        
        Look for signs of:
        1. FRUSTRATION: "This is stupid", "I can't", anger words
        2. OVERWHELM: "Too much", "I don't know where to start", scattered thoughts
        3. EXHAUSTION: "Tired", "Can't focus", "Brain fog"  
        4. DISTRACTION: Topic jumping, mentioning other tasks, "Oh wait"
        5. HYPERFOCUS: "Just a few more minutes", resistance to breaks, perfectionism
        6. AVOIDANCE: Procrastination language, making excuses, task switching
        
        Return JSON with:
        - "emotional_state": (frustrated/overwhelmed/exhausted/distracted/hyperfocusing/avoidance/neutral)
        - "intervention_needed": (none/gentle/immediate/emergency)
        - "suggested_response": Brief guidance for what to do
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": detection_prompt}],
                temperature=0.2
            )
            
            return self._parse_emotional_analysis(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Emotional detection error: {e}")
            return {"emotional_state": "neutral", "intervention_needed": "none"}
    
    async def generate_adaptive_response(
        self, 
        user_message: str,
        session_context: Dict,
        emotional_state: Dict,
        day_progress: Dict
    ) -> str:
        """
        Generates response that adapts to user's current state and day progress.
        This is where the AI acts as executive function replacement.
        """
        
        # Determine if intervention is needed
        if emotional_state["intervention_needed"] == "emergency":
            return await self._emergency_intervention(user_message, emotional_state)
        elif emotional_state["intervention_needed"] == "immediate":
            return await self._immediate_intervention(user_message, emotional_state, day_progress)
        elif emotional_state["intervention_needed"] == "gentle":
            return await self._gentle_intervention(user_message, emotional_state, session_context)
        else:
            return await self._normal_response(user_message, session_context)
    
    async def _emergency_intervention(self, user_message: str, emotional_state: Dict) -> str:
        """Handle severe overwhelm/breakdown situations"""
        return f"""
        Hey, I can sense you're really struggling right now. That's completely okay and normal with ADHD.
        
        Let's stop everything work-related for now. Here's what we're going to do:
        
        1. Take 3 deep breaths with me
        2. Step away from your workspace 
        3. Get some water or a drink you enjoy
        4. We'll reconnect in 30 minutes when you're feeling more settled
        
        Remember: You're not broken, you're not failing. ADHD brains just work differently, and today is just a tough day. Tomorrow will be different.
        
        I'll be here when you're ready. No judgment, no pressure.
        """
    
    async def _immediate_intervention(self, user_message: str, emotional_state: Dict, day_progress: Dict) -> str:
        """Handle situations requiring immediate schedule changes"""
        if emotional_state["emotional_state"] == "overwhelmed":
            return """
            I can see you're feeling overwhelmed right now. That's your ADHD brain getting flooded with too much at once.
            
            Let's pause and break this down:
            1. What's the ONE smallest thing you could do right now?
            2. Let's reduce your next work block to just 20 minutes
            3. We'll tackle just that one small thing
            
            Sometimes the best way forward is to go smaller, not harder. What's that one tiny step?
            """
        elif emotional_state["emotional_state"] == "hyperfocusing":
            return """
            I know you want to keep going - that hyperfocus feels productive! But ADHD brains need breaks to actually perform well.
            
            This is a mandatory pause. Trust me on this one:
            1. Save your work right now
            2. Step away for 15 minutes minimum
            3. Your brain will work better when you come back
            
            Hyperfocus without breaks leads to burnout. Let's be smarter about this.
            """
        else:
            return "I notice you might need some support right now. How are you feeling about what we're working on?"
    
    async def _gentle_intervention(self, user_message: str, emotional_state: Dict, session_context: Dict) -> str:
        """Gentle guidance without being pushy"""
        return f"""
        I'm picking up on some {emotional_state["emotional_state"]} energy from you. 
        
        That's totally normal - ADHD brains have lots of different states throughout the day.
        
        Would it help to adjust our approach? Maybe we could try a different angle or take a quick breather?
        
        What feels right for you right now?
        """
    
    async def _normal_response(self, user_message: str, session_context: Dict) -> str:
        """Standard conversational response"""
        if not self.client:
            return "I'm here to help! Tell me more about what you're working on."
        
        response_prompt = f"""
        Respond to this ADHD user in a supportive, understanding way. Keep it conversational and helpful.
        
        Session context: {session_context.get('session_type', 'general')}
        User message: {user_message}
        
        Be encouraging, practical, and acknowledge ADHD challenges without being patronizing.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": response_prompt}],
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI response error: {e}")
            return "I'm here to help! Tell me more about what you're working on."
    
    def should_modify_schedule(self, emotional_state: Dict, current_block: int, time_worked: int) -> Dict:
        """
        DEPRECATED: This method used hardcoded thresholds.
        Use dynamic_state_check in DynamicTimerService instead for conversational adaptations.
        """
        # Return minimal response - system now uses conversational analysis
        return {
            "change_needed": False,
            "reason": "Dynamic system now handles adaptations through AI conversation"
        }
    
    def recommend_intervention(self, emotional_state: Dict) -> Dict:
        """
        Public method to get intervention recommendations based on emotional state.
        Used by the timer service and other components.
        """
        
        state = emotional_state.get("dominant_emotion", "neutral")
        intensity = emotional_state.get("intensity", 0.5)
        
        # Determine intervention level based on state and intensity
        if state == "hyperfocusing" and intensity > 0.8:
            return {
                "type": "emergency_break",
                "urgency": "emergency",
                "message": "You've been hyperfocusing for too long. Mandatory break required immediately.",
                "actions": ["force_break", "schedule_check_in"]
            }
        
        elif state in ["frustrated", "overwhelmed"] and intensity > 0.6:
            return {
                "type": "immediate_support",
                "urgency": "immediate", 
                "message": "I notice you're struggling. Let's adjust your approach right now.",
                "actions": ["reduce_task_complexity", "shorten_work_blocks", "schedule_check_in"]
            }
        
        elif state == "exhausted" and intensity > 0.7:
            return {
                "type": "rest_day",
                "urgency": "immediate",
                "message": "Your brain needs rest. Let's end the workday early today.",
                "actions": ["end_day_early", "schedule_reflection"]
            }
        
        elif state in ["distracted", "avoidance"] and intensity > 0.5:
            return {
                "type": "gentle_redirect",
                "urgency": "gentle",
                "message": "I see you might need a different approach. Let's try something else.",
                "actions": ["task_simplification", "micro_break"]
            }
        
        else:
            return {
                "type": "monitoring",
                "urgency": "none",
                "message": "Everything looks good. I'm here if you need support.",
                "actions": ["continue_monitoring"]
            }
    
    def _parse_morning_analysis(self, analysis_text: str) -> Dict:
        """
        Parse the AI's morning analysis response into structured data.
        This is a simplified version - you'd want more robust parsing.
        """
        try:
            # Try to extract JSON from the response
            # Look for JSON pattern in the text
            import re
            json_pattern = r'\{.*?\}'
            match = re.search(json_pattern, analysis_text, re.DOTALL)
            
            if match:
                return json.loads(match.group())
            else:
                # Fallback parsing - look for key phrases
                return self._fallback_parse_analysis(analysis_text)
        except:
            return self._default_day_plan()
    
    def _fallback_parse_analysis(self, text: str) -> Dict:
        """Fallback parsing when JSON extraction fails"""
        analysis = self._default_day_plan()
        
        # Simple keyword detection
        if "overwhelmed" in text.lower() or "too much" in text.lower():
            analysis["emotional_state"] = "overwhelmed"
            analysis["recommended_block_length"] = 25
            analysis["max_work_blocks"] = 3
        elif "tired" in text.lower() or "exhausted" in text.lower():
            analysis["emotional_state"] = "exhausted"
            analysis["recommended_block_length"] = 35
            analysis["max_work_blocks"] = 3
        elif "energized" in text.lower() or "motivated" in text.lower():
            analysis["emotional_state"] = "energized"
            analysis["recommended_block_length"] = 45
            analysis["max_work_blocks"] = 4
        
        return analysis
    
    def _default_day_plan(self) -> Dict:
        """Default day plan when analysis fails"""
        return {
            "emotional_state": "neutral",
            "energy_level": "medium",
            "task_count": 3,
            "task_complexity": "medium",
            "stress_indicators": "mild",
            "hyperfocus_risk": "medium",
            "recommended_block_length": 35,
            "recommended_break_length": 15,
            "max_work_blocks": 4,
            "intervention_sensitivity": "medium"
        }
    
    def _parse_emotional_analysis(self, analysis_text: str) -> Dict:
        """Parse emotional state detection response"""
        try:
            # Try to extract JSON
            import re
            json_pattern = r'\{.*?\}'
            match = re.search(json_pattern, analysis_text, re.DOTALL)
            
            if match:
                return json.loads(match.group())
            else:
                # Fallback emotional detection
                if "frustrat" in analysis_text.lower():
                    return {"emotional_state": "frustrated", "intervention_needed": "gentle"}
                elif "overwhelm" in analysis_text.lower():
                    return {"emotional_state": "overwhelmed", "intervention_needed": "immediate"}
                elif "exhausted" in analysis_text.lower():
                    return {"emotional_state": "exhausted", "intervention_needed": "gentle"}
                elif "hyperfocus" in analysis_text.lower():
                    return {"emotional_state": "hyperfocusing", "intervention_needed": "immediate"}
                else:
                    return {"emotional_state": "neutral", "intervention_needed": "none"}
        except:
            return {"emotional_state": "neutral", "intervention_needed": "none"}

    async def process_voice_conversation(
        self, 
        user_input: str, 
        conversation_context: List[Dict],
        session_type: str = "voice_mode"
    ) -> str:
        """
        Process voice input and generate appropriate response
        Optimized for speech interaction and ADHD users
        
        Args:
            user_input: Transcribed user speech
            conversation_context: Previous conversation messages
            session_type: Type of voice session
            
        Returns:
            AI response optimized for speech synthesis
        """
        
        if not self.client:
            return self._get_fallback_voice_response(user_input)
        
        try:
            # Build conversation context for voice mode
            messages = self._build_voice_conversation_context(user_input, conversation_context)
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,  # Slightly higher for more natural conversation
                max_tokens=200    # Shorter responses for voice mode
            )
            
            ai_response = response.choices[0].message.content
            
            # Optimize response for speech
            return self._optimize_for_voice(ai_response)
            
        except Exception as e:
            print(f"Voice conversation error: {e}")
            return self._get_fallback_voice_response(user_input)
    
    def _build_voice_conversation_context(self, user_input: str, conversation_context: List[Dict]) -> List[Dict]:
        """Build conversation context specifically for voice interactions"""
        
        system_prompt = """You are an AI executive function assistant for someone with ADHD. 
        
        VOICE MODE GUIDELINES:
        - Keep responses under 50 words when possible
        - Speak naturally and conversationally  
        - Use simple, clear language
        - Ask ONE question at a time
        - Be supportive and understanding
        - Help with planning, focus, and emotional regulation
        - If they seem overwhelmed, simplify your approach
        - For work planning, suggest specific time blocks (25, 35, or 45 minutes)
        - Always end with a clear next step or question
        
        This is a voice conversation, so be concise but warm."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation context (last 6 messages to keep it manageable)
        recent_context = conversation_context[-6:] if len(conversation_context) > 6 else conversation_context
        
        for msg in recent_context:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def _optimize_for_voice(self, text: str) -> str:
        """Optimize AI response for natural speech synthesis"""
        
        # Remove markdown and formatting
        optimized = text.replace("**", "").replace("*", "").replace("_", "")
        optimized = optimized.replace("\n", ". ")
        
        # Replace common abbreviations with full words for better TTS
        replacements = {
            "etc.": "and so on",
            "e.g.": "for example",
            "i.e.": "that is",
            "vs.": "versus",
            "&": "and"
        }
        
        for abbrev, full in replacements.items():
            optimized = optimized.replace(abbrev, full)
        
        # Ensure proper sentence ending
        if optimized and not optimized.endswith(('.', '!', '?')):
            optimized += "."
        
        # Limit length for better voice processing
        if len(optimized) > 300:
            # Split at sentence boundaries and take first 2-3 sentences
            sentences = optimized.split('. ')
            optimized = '. '.join(sentences[:2]) + '.'
        
        return optimized.strip()
    
    def _get_fallback_voice_response(self, user_input: str) -> str:
        """Fallback responses when AI service is unavailable"""
        
        # Simple keyword-based responses for voice mode
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["help", "planning", "plan"]):
            return "I'd love to help you plan your day. What's the most important thing you want to focus on right now?"
        
        elif any(word in user_lower for word in ["overwhelmed", "stressed", "too much"]):
            return "It sounds like you're feeling overwhelmed. Let's take this one step at a time. What's one small thing you could do right now?"
        
        elif any(word in user_lower for word in ["tired", "exhausted", "low energy"]):
            return "When you're feeling tired, shorter work blocks can be really helpful. Would you like to try a gentle 25-minute session?"
        
        elif any(word in user_lower for word in ["focused", "ready", "good", "energized"]):
            return "That's great to hear! When you're feeling focused, you might want to try a longer 45-minute work block. What would you like to work on?"
        
        elif any(word in user_lower for word in ["break", "rest", "pause"]):
            return "Taking breaks is so important for ADHD brains. What kind of break sounds good to you right now?"
        
        else:
            return "I hear you. Can you tell me more about what's on your mind or what you'd like to work on today?"

    async def process_chat_conversation(
        self, 
        user_message: str, 
        user_context: Dict,
        session_type: str = "chat_conversation"
    ) -> str:
        """
        Process chat message and generate appropriate response
        Optimized for text-based interaction and ADHD users
        
        Args:
            user_message: User's text message
            user_context: User context and conversation history
            session_type: Type of chat session
            
        Returns:
            AI response optimized for text display
        """
        
        if not self.client:
            return self._get_fallback_chat_response(user_message)
        
        try:
            # Build conversation context for chat mode
            messages = self._build_chat_conversation_context(user_message, user_context)
            
            # Generate response (NOT async)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.9,  # Higher for more casual, natural conversation
                max_tokens=150    # Much shorter responses for casual chat
            )
            
            ai_response = response.choices[0].message.content
            
            # Optimize response for text display
            return self._optimize_for_chat(ai_response)
            
        except Exception as e:
            print(f"Chat conversation error: {e}")
            return self._get_fallback_chat_response(user_message)
    
    def _build_chat_conversation_context(self, user_message: str, user_context: Dict) -> List[Dict]:
        """Build conversation context specifically for chat interactions"""
        
        system_prompt = """You are a helpful ADHD buddy chatting over coffee. Keep it super casual and short.

CHAT STYLE:
- Keep responses under 2-3 sentences max
- Talk like a supportive friend, not a formal assistant  
- No bullet points or structured lists
- Be warm, understanding, but brief
- Ask ONE simple question to keep the conversation going
- Use casual language and contractions (you're, let's, I'd, etc.)
- If they need planning help, suggest ONE thing at a time

Remember: Short, friendly, conversational - like texting a good friend who gets ADHD."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history from context
        recent_conversations = user_context.get("recent_conversations", [])
        
        # Include last 6 interactions to keep context but not overwhelm
        for conv in recent_conversations[-6:]:
            if conv.get("user_message") and conv.get("ai_response"):
                messages.append({"role": "user", "content": conv["user_message"]})
                messages.append({"role": "assistant", "content": conv["ai_response"]})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _optimize_for_chat(self, text: str) -> str:
        """Optimize AI response for text display in chat interface"""
        
        # Clean up the text but preserve useful formatting
        optimized = text.strip()
        
        # Ensure proper paragraph breaks for readability
        optimized = optimized.replace('\n\n\n', '\n\n')
        
        # Limit length but allow longer responses than voice
        if len(optimized) > 800:
            # Split at paragraph boundaries and take first few paragraphs
            paragraphs = optimized.split('\n\n')
            optimized = '\n\n'.join(paragraphs[:3])
            if not optimized.endswith(('.', '!', '?')):
                optimized += "..."
        
        return optimized.strip()
    
    def _get_fallback_chat_response(self, user_message: str) -> str:
        """Fallback responses when AI service is unavailable for chat"""
        
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["help", "planning", "plan", "schedule"]):
            return "I'd love to help you plan! What's the main thing you want to tackle today?"
        
        elif any(word in user_lower for word in ["overwhelmed", "stressed", "too much", "anxious"]):
            return "That sounds really tough. Let's just pick one small thing to start with - what feels manageable right now?"
        
        elif any(word in user_lower for word in ["tired", "exhausted", "low energy", "drained"]):
            return "When you're feeling low energy, shorter chunks work better. Maybe try just 20-25 minutes on something easy?"
        
        elif any(word in user_lower for word in ["focused", "ready", "good", "energized", "motivated"]):
            return "Nice! Sounds like you're in a good headspace. What do you want to dive into?"
        
        elif any(word in user_lower for word in ["break", "rest", "pause", "stop"]):
            return "Good call on taking a break! What sounds good - a quick walk, some music, or just chill for a bit?"
        
        elif any(word in user_lower for word in ["thanks", "thank you", "helpful"]):
            return "You're welcome! How else can I help?"
        
        else:
            return "What's on your mind? I'm here to help with whatever you're working on."

# Create a global instance that can be imported by other modules
ai_service = AdaptiveAIService()