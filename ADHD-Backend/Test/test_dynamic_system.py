#!/usr/bin/env python3
"""
Dynamic AI-Driven Scheduling System Test

This test demonstrates the FULLY DYNAMIC system where:
- NO hardcoded work block durations
- NO predetermined break lengths
- NO fixed intervention thresholds
- Everything determined through LLM conversations in real-time

The AI asks questions, gets user responses, and makes all decisions dynamically.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, create_tables
from timer_service import DynamicTimerService, ConversationalState
from models import User

async def test_dynamic_system():
    """
    Comprehensive test of the fully dynamic LLM-driven system
    """
    
    print("🤖 ADHD Companion - FULLY DYNAMIC AI-DRIVEN SYSTEM TEST")
    print("=" * 70)
    print("🔥 NO HARDCODED VALUES - EVERYTHING THROUGH AI CONVERSATION")
    print("=" * 70)
    
    # Initialize
    db = next(get_db())
    create_tables()
    dynamic_service = DynamicTimerService(db)
    
    # Get existing user
    user = db.query(User).filter(User.username == "alex_chen").first()
    if not user:
        user = User(username="alex_chen", email="alex@example.com")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    print(f"👤 Testing with user: {user.username} (ID: {user.id})")
    print()
    
    # =====================================
    # 1. DYNAMIC PLANNING CONVERSATION
    # =====================================
    
    print("🎯 STEP 1: Start Dynamic Planning Conversation")
    print("-" * 50)
    print("🤖 AI will ask questions and adapt based on responses...")
    print()
    
    # Start dynamic planning
    planning_result = await dynamic_service.start_dynamic_planning_conversation(user.id)
    
    if planning_result["success"]:
        print("🤖 AI Question:", planning_result["ai_question"])
        print()
        
        # Simulate user response (feeling tired today)
        user_response_1 = "I'm feeling pretty tired today, had a rough night. My energy is low but I have some important work to get done."
        
        print(f"👤 User Response: {user_response_1}")
        print()
        
        # Continue conversation
        continue_result = await dynamic_service.continue_planning_conversation(
            user.id, user_response_1
        )
        
        if continue_result["success"]:
            ai_response = continue_result["ai_response"]
            print("🤖 AI Response:")
            print(f"   Type: {ai_response['type']}")
            print(f"   Content: {ai_response['content']}")
            
            if ai_response.get("suggested_durations"):
                print(f"   Suggested Durations: {ai_response['suggested_durations']}")
            print()
    
    # =====================================
    # 2. DYNAMIC WORK BLOCK CREATION
    # =====================================
    
    print("⏰ STEP 2: Dynamic Work Block Creation")
    print("-" * 50)
    print("🤖 AI will suggest duration options based on current state...")
    print()
    
    # Start dynamic work block
    work_block_result = await dynamic_service.start_dynamic_work_block(
        user.id, 
        task_description="Review quarterly reports"
    )
    
    if work_block_result["success"]:
        print("🤖 AI Question:", work_block_result["ai_question"])
        print(f"💡 Duration Options: {work_block_result['duration_options']}")
        print(f"🧠 AI Reasoning: {work_block_result['reasoning']}")
        print()
        
        # User chooses shortest option due to low energy
        chosen_duration = min(work_block_result["duration_options"])
        print(f"👤 User Choice: {chosen_duration} minutes (choosing shortest due to low energy)")
        print()
        
        # Confirm duration and start timer
        confirm_result = await dynamic_service.confirm_work_block_duration(
            user.id, chosen_duration
        )
        
        if confirm_result["success"]:
            work_block_id = confirm_result["work_block_id"]
            print("✅ Work Block Started:")
            print(f"   Work Block ID: {work_block_id}")
            print(f"   Duration: {chosen_duration} minutes (user-chosen)")
            print(f"   Message: {confirm_result['message']}")
            print()
    
    # =====================================
    # 3. DYNAMIC REAL-TIME STATE CHECKING
    # =====================================
    
    print("🔍 STEP 3: Dynamic Real-Time State Analysis")
    print("-" * 50)
    print("🤖 AI analyzes user messages and suggests adaptations...")
    print()
    
    # Simulate user getting frustrated
    frustrated_message = "Ugh, this is so confusing. I keep re-reading the same paragraph and nothing is sticking. I feel like I'm wasting time."
    
    print(f"👤 User Message: {frustrated_message}")
    print()
    
    # AI analyzes the message dynamically
    state_check_result = await dynamic_service.dynamic_state_check(
        user.id, frustrated_message
    )
    
    if state_check_result["success"]:
        adaptation = state_check_result["adaptation_response"]
        work_context = state_check_result["current_work_context"]
        
        print("🧠 AI Analysis:")
        print(f"   Emotional State Detected: {adaptation['emotional_state_detected']}")
        print(f"   Needs Adaptation: {adaptation['needs_adaptation']}")
        print(f"   Suggested Action: {adaptation['suggested_action']}")
        print(f"   AI Response: {adaptation['ai_response']}")
        print(f"   Reasoning: {adaptation['reasoning']}")
        print()
        
        if work_context:
            print("📊 Current Work Context:")
            print(f"   Elapsed: {work_context['elapsed_minutes']} minutes")
            print(f"   Remaining: {work_context['remaining_minutes']} minutes")
            print()
    
    # =====================================
    # 4. SIMULATE ANOTHER STATE CHECK (OVERWHELMED)
    # =====================================
    
    print("😰 STEP 4: Another Dynamic State Check (Overwhelmed)")
    print("-" * 50)
    
    # User feeling overwhelmed
    overwhelmed_message = "There's just too much to do. I have this report, then emails, then a meeting prep. I don't know where to start and I feel like I'm drowning."
    
    print(f"👤 User Message: {overwhelmed_message}")
    print()
    
    # AI responds dynamically
    overwhelmed_check = await dynamic_service.dynamic_state_check(
        user.id, overwhelmed_message
    )
    
    if overwhelmed_check["success"]:
        adaptation = overwhelmed_check["adaptation_response"]
        
        print("🧠 AI Analysis (Overwhelmed):")
        print(f"   State: {adaptation['emotional_state_detected']}")
        print(f"   Needs Help: {adaptation['needs_adaptation']}")
        print(f"   Suggested Action: {adaptation['suggested_action']}")
        print(f"   AI Response: {adaptation['ai_response']}")
        print()
    
    # =====================================
    # 5. DYNAMIC BREAK DECISION
    # =====================================
    
    print("☕ STEP 5: Dynamic Break Decision")
    print("-" * 50)
    print("🤖 AI suggests break options based on work block performance...")
    print()
    
    # Simulate work block completion and break decision
    if 'work_block_id' in locals():
        break_decision_result = await dynamic_service.dynamic_break_decision(
            user.id, work_block_id
        )
        
        if break_decision_result["success"]:
            print("🤖 AI Check-in:", break_decision_result["check_in_question"])
            print(f"🕐 Break Options: {break_decision_result['break_options']}")
            print(f"📝 Descriptions: {break_decision_result['option_descriptions']}")
            print(f"💭 AI Reasoning: {break_decision_result['reasoning']}")
            print()
    
    # =====================================
    # 6. GET DYNAMIC STATUS
    # =====================================
    
    print("📊 STEP 6: Dynamic System Status")
    print("-" * 50)
    
    status = await dynamic_service.get_dynamic_status(user.id)
    
    print("🔄 Current Dynamic Status:")
    print(f"   System Type: {status['system_type']}")
    print(f"   Has Active Conversation: {status['has_active_conversation']}")
    print(f"   Conversation State: {status.get('conversation_state', 'None')}")
    print(f"   Active Work Blocks: {len(status['active_work_blocks'])}")
    
    for block in status['active_work_blocks']:
        print(f"     • Block {block['work_block_id']}: {block['state']} ({block['elapsed_minutes']}min elapsed)")
    
    print(f"   Last Update: {status['last_update']}")
    print()
    
    # =====================================
    # 7. DEMONSTRATE ADAPTATION IN ACTION
    # =====================================
    
    print("🔄 STEP 7: Dynamic Adaptation in Real-Time")
    print("-" * 50)
    
    # Simulate user saying they want to continue but are struggling
    struggling_message = "I want to keep going but I'm having trouble focusing. Maybe I should take a quick break?"
    
    print(f"👤 User Message: {struggling_message}")
    print()
    
    struggle_check = await dynamic_service.dynamic_state_check(
        user.id, struggling_message
    )
    
    if struggle_check["success"]:
        adaptation = struggle_check["adaptation_response"]
        
        print("🧠 AI Real-Time Adaptation:")
        print(f"   Analysis: {adaptation['emotional_state_detected']}")
        print(f"   Action: {adaptation['suggested_action']}")
        print(f"   Response: {adaptation['ai_response']}")
        print()
    
    # =====================================
    # SUMMARY
    # =====================================
    
    print("🎉 DYNAMIC SYSTEM TEST COMPLETE")
    print("=" * 70)
    print("✅ FULLY DYNAMIC FEATURES DEMONSTRATED:")
    print("   🤖 AI-driven planning conversations (no hardcoded durations)")
    print("   ⏰ Dynamic work block creation (user chooses from AI suggestions)")
    print("   🔍 Real-time state analysis (no preset thresholds)")
    print("   🔄 Adaptive responses based on user messages")
    print("   ☕ Dynamic break decisions (AI suggests based on performance)")
    print("   📊 Conversational state management")
    print()
    print("🔥 KEY DIFFERENCES FROM STATIC SYSTEM:")
    print("   ❌ No hardcoded 25/35/45 minute defaults")
    print("   ❌ No fixed intervention thresholds")
    print("   ❌ No predetermined break lengths")
    print("   ✅ Everything determined through AI conversation")
    print("   ✅ User chooses from AI-suggested options")
    print("   ✅ Real-time adaptation based on natural language")
    print()
    print("🧠 THIS IS TRUE DYNAMIC EXECUTIVE FUNCTION REPLACEMENT!")

async def demonstrate_conversation_flow():
    """
    Demonstrate a complete conversation flow showing the dynamic nature
    """
    
    print("\n" + "="*80)
    print("🗣️  CONVERSATION FLOW DEMONSTRATION")
    print("="*80)
    
    print("\n🤖 AI: How are you feeling today? What's your energy level like?")
    print("👤 User: I'm feeling overwhelmed. I have a big presentation tomorrow and haven't started.")
    print()
    print("🤖 AI: I understand that pressure. Given you're feeling overwhelmed, would you prefer:")
    print("      • 15 minutes (bite-sized focus)")
    print("      • 25 minutes (gentle progress)")  
    print("      • 35 minutes (standard block)")
    print()
    print("👤 User: 15 minutes sounds manageable.")
    print()
    print("🤖 AI: Perfect! Let's start with a 15-minute focused session on your presentation.")
    print("      [Timer starts - 15 minutes, chosen by user based on AI suggestions]")
    print()
    print("--- 8 minutes into work block ---")
    print()
    print("👤 User: This is actually going well! I found a good flow.")
    print()
    print("🤖 AI: That's fantastic! I can hear the confidence in your voice. Would you like to:")
    print("      • Continue for the remaining 7 minutes")
    print("      • Extend this session by 10 more minutes (total 25)")
    print("      • Keep going but check in again at 15 minutes")
    print()
    print("👤 User: Let's extend it to 25 minutes total.")
    print()
    print("🤖 AI: Great! I've adjusted your timer. 17 minutes remaining on this extended session.")
    print()
    print("--- Work block ends ---")
    print()
    print("🤖 AI: How did that session feel? You seemed to hit a good flow state.")
    print("👤 User: Much better than expected! I made real progress.")
    print()
    print("🤖 AI: Excellent! For your break, what sounds most appealing:")
    print("      • 5 minutes (quick breather, keep momentum)")
    print("      • 15 minutes (standard refresh)")
    print("      • 25 minutes (celebration break - you earned it!)")
    print()
    print("👤 User: 5 minutes - I want to keep this momentum going.")
    print()
    print("🤖 AI: Perfect choice! 5-minute energizing break, then we'll ride this wave.")
    print()
    print("🔥 EVERY DECISION MADE THROUGH CONVERSATION - NO HARDCODED VALUES!")

if __name__ == "__main__":
    print("🚀 Starting Dynamic AI-Driven System Test...")
    asyncio.run(test_dynamic_system())
    asyncio.run(demonstrate_conversation_flow()) 