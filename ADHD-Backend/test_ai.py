#!/usr/bin/env python3

import asyncio
from ai_service import ai_service

async def test_ai():
    print("=== Testing AI Service ===")
    print(f"Client exists: {ai_service.client is not None}")
    print(f"Model: {ai_service.model}")
    
    if ai_service.client:
        # Test different types of messages
        test_messages = [
            "i wanna prep for my exam",
            "feeling really overwhelmed today",
            "I'm tired but need to get work done",
            "hey what's up"
        ]
        
        for i, message in enumerate(test_messages):
            try:
                print(f"\n=== Test {i+1}: '{message}' ===")
                response = await ai_service.process_chat_conversation(
                    user_message=message,
                    user_context={
                        "user_id": 1, 
                        "recent_conversations": [], 
                        "conversation_mode": "chat"
                    }
                )
                print(f"AI Response: {response}")
                print(f"Length: {len(response)} chars")
                
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("No AI client available")

if __name__ == "__main__":
    asyncio.run(test_ai()) 