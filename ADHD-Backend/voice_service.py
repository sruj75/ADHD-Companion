import os
import io
import base64
from typing import Optional, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class VoiceService:
    """Voice service handling Speech-to-Text and Text-to-Speech with Groq APIs"""
    
    def __init__(self):
        # Initialize Groq client with hardcoded API key for immediate functionality
        # Replace with your actual GROQ API key from https://console.groq.com/keys
        groq_api_key = "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"  # Hardcoded GROQ API key
        
        if groq_api_key and groq_api_key != "your_groq_api_key_here" and groq_api_key != "gsk_PUT_YOUR_ACTUAL_GROQ_API_KEY_HERE":
            self.groq_client = Groq(api_key=groq_api_key)
            print("✅ Voice service initialized with Groq API")
        else:
            # Fallback to environment variable if hardcoded key is placeholder
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if groq_api_key:
                self.groq_client = Groq(api_key=groq_api_key)
                print("✅ Voice service initialized with Groq API from environment")
            else:
                self.groq_client = None
                print("⚠️ GROQ_API_KEY not found - Voice services will be unavailable")
        
        # Default voice configurations based on Groq documentation
        self.default_stt_model = "whisper-large-v3-turbo"  # Best price/performance for multilingual
        self.default_tts_model = "playai-tts"  # Groq TTS model
        self.default_voice = "Calum-PlayAI"  # Calm, clear voice good for ADHD
        
        # ADHD-optimized settings
        self.stt_temperature = 0.0  # Most consistent transcription
    
    @property
    def client(self):
        """Alias for groq_client for compatibility"""
        return self.groq_client
        
    async def speech_to_text(
        self, 
        audio_data: bytes, 
        language: Optional[str] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert speech audio to text using Groq Whisper models
        
        Args:
            audio_data: Raw audio bytes (any format supported by Whisper)
            language: Language code (ISO-639-1) for better accuracy, or 'auto' for detection
            model: Whisper model to use
            
        Returns:
            Dict with transcription results and metadata
        """
        
        if not self.groq_client:
            return {
                "success": False,
                "error": "Groq API key not configured",
                "text": "",
                "fallback_message": "Speech recognition unavailable. Please check configuration."
            }
        
        try:
            # Use provided settings or defaults
            stt_model = model or self.default_stt_model
            lang = language or "en"  # Default to English
            
            # Create audio file-like object for Groq API
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"  # Groq needs a filename
            
            # Transcribe using Groq Whisper
            transcription = self.groq_client.audio.transcriptions.create(
                file=("audio.wav", audio_file),  # Groq expects a tuple with filename and file object
                model=stt_model,
                language=lang,
                temperature=self.stt_temperature,
                response_format="verbose_json"  # Get more metadata
            )
            
            return {
                "success": True,
                "text": transcription.text,
                "language": lang,
                "model_used": stt_model,
                "metadata": {
                    "duration": getattr(transcription, 'duration', None),
                    "segments": getattr(transcription, 'segments', [])
                }
            }
            
        except Exception as e:
            print(f"STT Error: {e}")
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
        model: Optional[str] = None,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Convert text to speech using Groq TTS
        
        Args:
            text: Text to convert to speech
            voice: Voice ID to use
            model: TTS model to use
            speed: Speech speed (0.25 to 4.0, default 1.0)
            
        Returns:
            Dict with audio data and metadata
        """
        
        if not self.groq_client:
            return {
                "success": False,
                "error": "Groq API key not configured",
                "fallback_message": f"Sorry, I couldn't generate speech for: {text}"
            }
        
        try:
            # Use provided settings or defaults
            tts_model = model or self.default_tts_model
            voice_id = voice or self.default_voice
            
            # Optimize text for speech (ADHD-friendly)
            optimized_text = self.optimize_text_for_speech(text)
            
            # Generate speech using correct Groq TTS syntax
            response = self.groq_client.audio.speech.create(
                model=tts_model,
                voice=voice_id,
                input=optimized_text,
                response_format="wav"
            )
            
            # Get audio content as bytes - handle the response properly
            if hasattr(response, 'content'):
                audio_data = response.content
            elif hasattr(response, 'read'):
                audio_data = response.read()
            else:
                # Try to access as bytes directly
                audio_data = bytes(response)
            
            return {
                "success": True,
                "audio_data": audio_data,
                "audio_base64": base64.b64encode(audio_data).decode('utf-8'),
                "text": optimized_text,
                "voice_used": voice_id,
                "model_used": tts_model,
                "format": "wav",
                "provider": "groq"
            }
            
        except Exception as e:
            print(f"Groq TTS Error: {e}")
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
        
        # Clean up extra spaces
        optimized = " ".join(optimized.split())
        
        # Limit length for better TTS processing (Groq recommends shorter chunks)
        if len(optimized) > 500:
            # Split at sentence boundaries
            sentences = optimized.split('. ')
            # Take first 3-4 sentences for optimal TTS
            optimized = '. '.join(sentences[:3]) + '.'
        
        return optimized.strip()
    
    def get_available_voices(self) -> Dict[str, list]:
        """Return available voices for different models based on Groq documentation"""
        return {
            "playai-tts": [
                "Arista-PlayAI",    # Female, professional
                "Atlas-PlayAI",     # Male, confident  
                "Basil-PlayAI",     # Male, storyteller
                "Briggs-PlayAI",    # Male, narrator
                "Calum-PlayAI",     # Male, calm (default)
                "Celeste-PlayAI",   # Female, warm
                "Cheyenne-PlayAI",  # Female, energetic
                "Chip-PlayAI",      # Male, casual
                "Cillian-PlayAI",   # Male, conversational
                "Deedee-PlayAI",    # Female, friendly
                "Fritz-PlayAI",     # Male, formal
                "Gail-PlayAI",      # Female, professional
                "Indigo-PlayAI",    # Non-binary, neutral
                "Mamaw-PlayAI",     # Female, elderly
                "Mason-PlayAI",     # Male, friendly
                "Mikail-PlayAI",    # Male, deep
                "Mitch-PlayAI",     # Male, casual
                "Quinn-PlayAI",     # Neutral, gentle
                "Thunder-PlayAI"    # Male, powerful
            ],
            "playai-tts-arabic": [
                "Ahmad-PlayAI",     # Male, Arabic
                "Amira-PlayAI",     # Female, Arabic
                "Khalid-PlayAI",    # Male, Arabic
                "Nasser-PlayAI"     # Male, Arabic
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
            "gentle": "Quinn-PlayAI",
            "energetic": "Cheyenne-PlayAI",
            "storyteller": "Basil-PlayAI"
        }
        
        return voice_map.get(user_preference, self.default_voice)
    
    def get_stt_model_recommendation(self, use_case: str = "general") -> str:
        """Get STT model recommendation based on use case"""
        model_map = {
            "general": "whisper-large-v3-turbo",  # Best price/performance
            "accuracy": "whisper-large-v3",       # Highest accuracy
            "english_only": "distil-whisper-large-v3-en",  # Fastest for English
            "realtime": "whisper-large-v3-turbo"  # Fast multilingual
        }
        
        return model_map.get(use_case, self.default_stt_model)

    def reinitialize_client(self):
        """Reinitialize the Groq client - useful after accepting terms"""
        groq_api_key = "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"
        
        if groq_api_key and groq_api_key != "your_groq_api_key_here" and groq_api_key != "gsk_PUT_YOUR_ACTUAL_GROQ_API_KEY_HERE":
            self.groq_client = Groq(api_key=groq_api_key)
            print("🔄 Voice service client reinitialized")
            return True
        else:
            # Fallback to environment variable
            groq_api_key = os.environ.get("GROQ_API_KEY")
            if groq_api_key:
                self.groq_client = Groq(api_key=groq_api_key)
                print("🔄 Voice service client reinitialized from environment")
                return True
            else:
                print("❌ Cannot reinitialize - no API key found")
                return False

# Global voice service instance
voice_service = VoiceService() 