import json
import base64
import io
import asyncio
from typing import Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect
from voice_service import voice_service
from ai_service import ai_service
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceWebSocketManager:
    """Manages WebSocket connections for voice interactions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_states: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept WebSocket connection and initialize session"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_states[session_id] = {
            "state": "idle",
            "audio_buffer": io.BytesIO(),
            "conversation_context": []
        }
        
        logger.info(f"Voice session {session_id} connected")
        
        # Send welcome message
        await self.send_message(session_id, {
            "type": "status",
            "state": "idle",
            "message": "Voice mode ready. Tap the circle to start talking."
        })
    
    async def disconnect(self, session_id: str):
        """Clean up WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.session_states:
            del self.session_states[session_id]
        logger.info(f"Voice session {session_id} disconnected")
    
    async def send_message(self, session_id: str, message: Dict):
        """Send message to specific WebSocket connection"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                await self.disconnect(session_id)
    
    async def handle_voice_session(self, websocket: WebSocket, session_id: str):
        """Main WebSocket message handler"""
        try:
            while True:
                # Receive message from client
                message_text = await websocket.receive_text()
                message = json.loads(message_text)
                
                await self.process_message(session_id, message)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for session {session_id}")
            await self.disconnect(session_id)
        except Exception as e:
            logger.error(f"Error in voice session {session_id}: {e}")
            await self.send_message(session_id, {
                "type": "error",
                "message": "An error occurred. Please try again."
            })
            await self.disconnect(session_id)
    
    async def process_message(self, session_id: str, message: Dict):
        """Process incoming WebSocket message"""
        message_type = message.get("type")
        session_state = self.session_states.get(session_id)
        
        if not session_state:
            return
        
        if message_type == "start_recording":
            await self.handle_start_recording(session_id)
            
        elif message_type == "audio_chunk":
            await self.handle_audio_chunk(session_id, message.get("data"))
            
        elif message_type == "stop_recording":
            await self.handle_stop_recording(session_id)
            
        elif message_type == "interrupt":
            await self.handle_interrupt(session_id)
            
        elif message_type == "set_voice":
            await self.handle_set_voice(session_id, message.get("voice"))
            
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def handle_start_recording(self, session_id: str):
        """Handle start of audio recording"""
        session_state = self.session_states[session_id]
        session_state["state"] = "listening"
        session_state["audio_buffer"] = io.BytesIO()  # Reset buffer
        
        await self.send_message(session_id, {
            "type": "status",
            "state": "listening",
            "message": "Listening... speak now"
        })
        
        logger.info(f"Session {session_id}: Started recording")
    
    async def handle_audio_chunk(self, session_id: str, audio_data: str):
        """Handle incoming audio chunk"""
        if not audio_data:
            return
            
        session_state = self.session_states[session_id]
        
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            session_state["audio_buffer"].write(audio_bytes)
            
            # Optional: Send acknowledgment that chunk was received
            # (Don't send too many of these to avoid flooding)
            
        except Exception as e:
            logger.error(f"Error processing audio chunk for {session_id}: {e}")
    
    async def handle_stop_recording(self, session_id: str):
        """Handle end of audio recording and process the complete audio"""
        session_state = self.session_states[session_id]
        session_state["state"] = "thinking"
        
        await self.send_message(session_id, {
            "type": "status", 
            "state": "thinking",
            "message": "Processing your message..."
        })
        
        # Get complete audio data
        audio_buffer = session_state["audio_buffer"]
        audio_buffer.seek(0)
        audio_data = audio_buffer.read()
        
        if len(audio_data) == 0:
            await self.send_message(session_id, {
                "type": "error",
                "message": "No audio received. Please try again."
            })
            session_state["state"] = "idle"
            return
        
        logger.info(f"Session {session_id}: Processing {len(audio_data)} bytes of audio")
        
        # Process the complete voice interaction
        await self.process_complete_voice_interaction(session_id, audio_data)
    
    async def process_complete_voice_interaction(self, session_id: str, audio_data: bytes):
        """Process complete voice interaction: STT -> AI -> TTS"""
        session_state = self.session_states[session_id]
        
        try:
            # Step 1: Speech-to-Text
            stt_result = await voice_service.speech_to_text(audio_data)
            
            if not stt_result["success"]:
                await self.send_message(session_id, {
                    "type": "error",
                    "message": stt_result.get("fallback_message", "Could not understand audio")
                })
                session_state["state"] = "idle"
                return
            
            user_text = stt_result["text"]
            logger.info(f"Session {session_id}: Transcribed: '{user_text}'")
            
            # Send transcription to client
            await self.send_message(session_id, {
                "type": "transcription",
                "text": user_text,
                "confidence": stt_result.get("confidence", "medium")
            })
            
            # Step 2: AI Processing
            ai_response = await self.get_ai_response(session_id, user_text)
            
            # Send AI response text
            await self.send_message(session_id, {
                "type": "ai_response",
                "text": ai_response
            })
            
            # Step 3: Text-to-Speech
            session_state["state"] = "speaking"
            await self.send_message(session_id, {
                "type": "status",
                "state": "speaking", 
                "message": "AI is responding..."
            })
            
            await self.generate_and_stream_speech(session_id, ai_response)
            
            # Reset to idle state
            session_state["state"] = "idle"
            await self.send_message(session_id, {
                "type": "status",
                "state": "idle",
                "message": "Ready for next message"
            })
            
        except Exception as e:
            logger.error(f"Error in voice interaction for {session_id}: {e}")
            await self.send_message(session_id, {
                "type": "error",
                "message": "Something went wrong processing your message. Please try again."
            })
            session_state["state"] = "idle"
    
    async def get_ai_response(self, session_id: str, user_input: str) -> str:
        """Get AI response for voice input"""
        session_state = self.session_states[session_id]
        
        # Add to conversation context
        session_state["conversation_context"].append({
            "role": "user",
            "content": user_input,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        # Get AI response using existing AI service
        # Note: This integrates with your existing dynamic AI conversation system
        try:
            # Use the existing AI service with voice context
            response = await ai_service.process_voice_conversation(
                user_input=user_input,
                conversation_context=session_state["conversation_context"],
                session_type="voice_mode"
            )
            
            # Add AI response to context
            session_state["conversation_context"].append({
                "role": "assistant", 
                "content": response,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"AI processing error for {session_id}: {e}")
            return "I'm having trouble processing that right now. Could you try asking in a different way?"
    
    async def generate_and_stream_speech(self, session_id: str, text: str):
        """Generate speech and stream to client"""
        try:
            # Get user's voice preference (default to calm)
            voice_preference = self.session_states[session_id].get("voice_preference", "calm")
            voice_id = voice_service.get_voice_recommendation(voice_preference)
            
            # Generate speech
            tts_result = await voice_service.text_to_speech(text, voice=voice_id)
            
            if not tts_result["success"]:
                await self.send_message(session_id, {
                    "type": "error",
                    "message": tts_result.get("fallback_message", "Could not generate speech")
                })
                return
            
            # Stream audio in chunks
            audio_data = tts_result["audio_data"]
            chunk_size = 4096  # 4KB chunks for smooth streaming
            
            for i in range(0, len(audio_data), chunk_size):
                chunk = audio_data[i:i + chunk_size]
                encoded_chunk = base64.b64encode(chunk).decode()
                is_final = i + chunk_size >= len(audio_data)
                
                await self.send_message(session_id, {
                    "type": "audio_chunk",
                    "data": encoded_chunk,
                    "is_final": is_final
                })
                
                # Small delay to prevent overwhelming the client
                await asyncio.sleep(0.02)  # 20ms delay
                
        except Exception as e:
            logger.error(f"TTS error for {session_id}: {e}")
            await self.send_message(session_id, {
                "type": "error",
                "message": "Could not generate speech response"
            })
    
    async def handle_interrupt(self, session_id: str):
        """Handle user interruption during AI speech"""
        session_state = self.session_states[session_id]
        session_state["state"] = "idle"
        
        await self.send_message(session_id, {
            "type": "status",
            "state": "idle",
            "message": "Ready to listen"
        })
        
        logger.info(f"Session {session_id}: User interrupted AI speech")
    
    async def handle_set_voice(self, session_id: str, voice_preference: str):
        """Update user's voice preference"""
        session_state = self.session_states[session_id]
        session_state["voice_preference"] = voice_preference
        
        voice_id = voice_service.get_voice_recommendation(voice_preference)
        
        await self.send_message(session_id, {
            "type": "voice_updated",
            "voice_preference": voice_preference,
            "voice_id": voice_id,
            "message": f"Voice set to {voice_preference}"
        })
        
        logger.info(f"Session {session_id}: Voice preference set to {voice_preference}")

# Global WebSocket manager instance
voice_websocket_manager = VoiceWebSocketManager() 