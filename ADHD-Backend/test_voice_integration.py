#!/usr/bin/env python3
"""
Test script for ADHD Companion Voice Integration (Phase 3)
Demonstrates STT, TTS, and WebSocket voice functionality
"""

import asyncio
import os
from voice_service import voice_service
from ai_service import ai_service

async def test_voice_services():
    """Test voice service functionality"""
    
    print("🎙️ Testing ADHD Companion Voice Integration")
    print("=" * 50)
    
    # Check if Groq API key is configured
    groq_key = os.environ.get("GROQ_API_KEY")
    if not groq_key or groq_key == "your_groq_api_key_here":
        print("⚠️  No GROQ_API_KEY found in environment")
        print("   Add your Groq API key to .env file to test actual STT/TTS")
        print("   Get one at: https://console.groq.com/")
        print()
        return
    
    print("✅ Groq API key configured")
    print()
    
    # Test 1: Available voices
    print("🔊 Available TTS Voices:")
    voices = voice_service.get_available_voices()
    for model, voice_list in voices.items():
        print(f"  {model}: {len(voice_list)} voices")
        for voice in voice_list[:3]:  # Show first 3
            print(f"    - {voice}")
        if len(voice_list) > 3:
            print(f"    ... and {len(voice_list) - 3} more")
    print()
    
    # Test 2: Voice recommendations
    print("🎯 Voice Recommendations:")
    preferences = ["calm", "professional", "friendly", "warm"]
    for pref in preferences:
        recommended = voice_service.get_voice_recommendation(pref)
        print(f"  {pref}: {recommended}")
    print()
    
    # Test 3: Text optimization for speech
    print("📝 Text Optimization for Speech:")
    sample_text = "**Hello!** I'm your AI assistant. Let's work on *planning* your day. Here are some options:\n- 25 minutes\n- 35 minutes\n- 45 minutes"
    optimized = voice_service.optimize_text_for_speech(sample_text)
    print(f"  Original: {repr(sample_text)}")
    print(f"  Optimized: {repr(optimized)}")
    print()
    
    # Test 4: AI voice response
    print("🤖 AI Voice Response Test:")
    try:
        conversation_context = [
            {"role": "user", "content": "I'm feeling overwhelmed today"},
            {"role": "assistant", "content": "I understand. Let's take this step by step."}
        ]
        
        response = await ai_service.process_voice_conversation(
            user_input="I need help planning my day",
            conversation_context=conversation_context
        )
        
        print(f"  User: 'I need help planning my day'")
        print(f"  AI: {repr(response)}")
        print(f"  Length: {len(response)} characters")
        print()
        
    except Exception as e:
        print(f"  AI Response Error: {e}")
        print()
    
    # Test 5: Mock TTS (without actual API call)
    print("🔊 TTS Configuration Test:")
    tts_config = {
        "model": voice_service.default_tts_model,
        "voice": voice_service.default_voice,
        "format": "wav"
    }
    print(f"  Default TTS Model: {tts_config['model']}")
    print(f"  Default Voice: {tts_config['voice']}")
    print(f"  Audio Format: {tts_config['format']}")
    print()
    
    print("✅ Voice integration test completed!")
    print()
    print("🚀 To test full functionality:")
    print("  1. Add your GROQ_API_KEY to .env file")
    print("  2. Run: uvicorn main:app --reload")
    print("  3. Test WebSocket: ws://localhost:8000/ws/voice/test-session")
    print("  4. Check API docs: http://localhost:8000/docs")

def test_websocket_message_flow():
    """Test WebSocket message handling logic"""
    print("📡 WebSocket Message Flow Test:")
    print("-" * 30)
    
    # Simulate message types
    message_types = [
        {"type": "start_recording", "description": "User starts speaking"},
        {"type": "audio_chunk", "data": "base64_audio_data", "description": "Audio data chunk"},
        {"type": "stop_recording", "description": "User stops speaking"},
        {"type": "interrupt", "description": "User interrupts AI response"},
        {"type": "set_voice", "voice": "calm", "description": "Change voice preference"}
    ]
    
    for msg in message_types:
        print(f"  {msg['type']}: {msg['description']}")
    
    print()
    
    # Simulate state flow
    print("🔄 Voice State Flow:")
    states = ["idle", "listening", "thinking", "speaking", "idle"]
    for i, state in enumerate(states):
        if i > 0:
            print(" → ", end="")
        print(state, end="")
    print()
    print()

if __name__ == "__main__":
    print("🎙️ ADHD Companion Voice Integration Test")
    print("Phase 3: Voice-First Interface with Groq APIs")
    print("=" * 60)
    print()
    
    # Test WebSocket flow
    test_websocket_message_flow()
    
    # Test voice services
    asyncio.run(test_voice_services()) 