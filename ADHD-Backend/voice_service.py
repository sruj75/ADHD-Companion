import os
import io
import base64
import asyncio
from typing import Optional, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class VoiceService:
    """Voice service handling Speech-to-Text and Text-to-Speech with Groq APIs"""
    
    def __init__(self):
        self.groq_client = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )
        
        # Default voice configurations
        self.default_stt_model = "whisper-large-v3-turbo"  # Fastest multilingual
        self.default_tts_model = "playai-tts"
        self.default_voice = "Calum-PlayAI"  # Calm, clear voice good for ADHD
        
        # ADHD-optimized settings
        self.stt_temperature = 0.0  # Most consistent transcription
        self.default_language = "en"
        
    async def speech_to_text(
        self, 
        audio_data: bytes, 
        language: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert audio bytes to text using Groq Whisper
        
        Args:
            audio_data: Audio file bytes (wav, mp3, etc.)
            language: Language code (ISO-639-1 format like 'en', 'es') 
            model: Whisper model to use
            
        Returns:
            Dict with transcription text and metadata
        """
        try:
            # Prepare audio file for Groq API
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"  # Groq needs a filename
            
            # Use provided settings or defaults
            stt_model = model or self.default_stt_model
            lang = language or self.default_language
            
            # Create transcription
            transcription = self.groq_client.audio.transcriptions.create(
                file=("audio.wav", audio_file.read()),
                model=stt_model,
                language=lang,
                temperature=self.stt_temperature,
                response_format="json"  # Simple format for now
            )
            
            return {
                "success": True,
                "text": transcription.text,
                "language": lang,
                "model_used": stt_model,
                "confidence": "high"  # Groq doesn't return confidence, assume high
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "fallback_message": "Sorry, I couldn't understand that. Could you try again?"
            }
    
    async def text_to_speech(
        self, 
        text: str, 
        voice: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert text to speech using Groq TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice ID to use
            model: TTS model to use
            
        Returns:
            Dict with audio data and metadata
        """
        try:
            # Use provided settings or defaults
            tts_model = model or self.default_tts_model
            voice_id = voice or self.default_voice
            
            # Optimize text for speech (ADHD-friendly)
            optimized_text = self.optimize_text_for_speech(text)
            
            # Generate speech
            speech_response = self.groq_client.audio.speech.create(
                model=tts_model,
                voice=voice_id,
                input=optimized_text,
                response_format="wav"  # Best compatibility
            )
            
            return {
                "success": True,
                "audio_data": speech_response.content,
                "text": optimized_text,
                "voice_used": voice_id,
                "model_used": tts_model,
                "format": "wav"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_message": f"Sorry, I couldn't generate speech for: {text}"
            }
    
    def optimize_text_for_speech(self, text: str) -> str:
        """
        Optimize text for natural speech output (ADHD-friendly)
        """
        # Remove markdown formatting
        optimized = text.replace("**", "").replace("*", "")
        optimized = optimized.replace("_", "")
        
        # Convert newlines to natural pauses
        optimized = optimized.replace("\n\n", ". ")
        optimized = optimized.replace("\n", ". ")
        
        # Ensure proper sentence endings
        if optimized and not optimized.endswith(('.', '!', '?')):
            optimized += "."
        
        # Add small pauses for better ADHD comprehension
        optimized = optimized.replace(". ", ". ... ")
        
        # Limit length for better processing (TTS works better with shorter chunks)
        if len(optimized) > 500:
            # Split at sentence boundaries
            sentences = optimized.split('. ')
            optimized = '. '.join(sentences[:3]) + '.'
        
        return optimized.strip()
    
    def get_available_voices(self) -> Dict[str, list]:
        """Return available voices for different models"""
        return {
            "playai-tts": [
                "Arista-PlayAI",    # Female, professional
                "Atlas-PlayAI",     # Male, confident  
                "Calum-PlayAI",     # Male, calm (default)
                "Celeste-PlayAI",   # Female, warm
                "Mason-PlayAI",     # Male, friendly
                "Quinn-PlayAI"      # Neutral, gentle
            ],
            "playai-tts-arabic": [
                "Ahmad-PlayAI",
                "Amira-PlayAI", 
                "Khalid-PlayAI",
                "Nasser-PlayAI"
            ]
        }
    
    def get_voice_recommendation(self, user_preference: str = "calm") -> str:
        """Get voice recommendation based on user preference"""
        voice_map = {
            "calm": "Calum-PlayAI",
            "professional": "Arista-PlayAI", 
            "friendly": "Mason-PlayAI",
            "warm": "Celeste-PlayAI",
            "confident": "Atlas-PlayAI",
            "gentle": "Quinn-PlayAI"
        }
        
        return voice_map.get(user_preference, self.default_voice)

# Global voice service instance
voice_service = VoiceService() 