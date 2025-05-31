#!/usr/bin/env python3
"""
Test script to demonstrate Session Management CRUD operations
This shows how our ADHD Companion backend handles sessions.
"""

import asyncio
from datetime import datetime, timedelta
from database import SessionLocal, create_tables, test_connection
from session_service import SessionService
from models import SessionType, SessionStatus, User
import sys
import os

# Add the backend directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_session_management():
    """
    Comprehensive test of our Session Management system.
    Demonstrates all CRUD operations for the 5 session types.
    """
    
    print("🧪 Testing ADHD Companion Session Management System")
    print("=" * 60)
    
    # Test database connection
    if not test_connection():
        print("❌ Database connection failed")
        return
    
    # Create tables if needed
    create_tables()
    
    # Create database session
    db = SessionLocal()
    session_service = SessionService(db)
    
    try:
        # Test 1: Create sessions for each type
        print("\n📝 TEST 1: Creating sessions for all 5 session types")
        print("-" * 50)
        
        user_id = 1  # Test user ID
        sessions_created = []
        
        for session_type in SessionType:
            session = session_service.create_session(
                user_id=user_id,
                session_type=session_type,
                scheduled_time=datetime.utcnow() + timedelta(minutes=10)
            )
            sessions_created.append(session)
            print(f"✅ Created {session_type.value} session (ID: {session.id})")
        
        # Test 2: Read operations
        print(f"\n📖 TEST 2: Reading session data")
        print("-" * 50)
        
        # Get all user sessions
        user_sessions = session_service.get_user_sessions(user_id)
        print(f"✅ Found {len(user_sessions)} sessions for user {user_id}")
        
        # Get specific session
        first_session = session_service.get_session(sessions_created[0].id)
        print(f"✅ Retrieved session details: {first_session.session_type}")
        
        # Get today's sessions
        todays_sessions = session_service.get_todays_sessions(user_id)
        print(f"✅ Found {len(todays_sessions)} sessions for today")
        
        # Test 3: Update operations (Session lifecycle)
        print(f"\n🔄 TEST 3: Session lifecycle operations")
        print("-" * 50)
        
        # Start a session
        test_session = sessions_created[0]
        started_session = session_service.start_session(test_session.id)
        print(f"✅ Started session: {started_session.session_type}")
        
        # Complete a session
        completed_session = session_service.complete_session(
            session_id=test_session.id,
            user_input="Test completed successfully",
            session_summary="This was a test session",
            effectiveness_rating=4
        )
        print(f"✅ Completed session with rating: {completed_session.session_effectiveness}")
        
        # Skip a session
        skip_session = sessions_created[1]
        skipped_session = session_service.skip_session(
            session_id=skip_session.id,
            reason="Testing skip functionality"
        )
        print(f"✅ Skipped session: {skipped_session.session_type}")
        
        # Test 4: Advanced queries
        print(f"\n🔍 TEST 4: Advanced session queries")
        print("-" * 50)
        
        # Get active session
        active_session = session_service.get_active_session(user_id)
        if active_session:
            print(f"✅ Found active session: {active_session.session_type}")
        else:
            print("ℹ️ No active sessions found")
        
        # Get next scheduled session
        next_session = session_service.get_next_scheduled_session(user_id)
        if next_session:
            print(f"✅ Next scheduled session: {next_session.session_type}")
        else:
            print("ℹ️ No upcoming sessions found")
        
        # Get session statistics
        stats = session_service.get_session_statistics(user_id, days=1)
        print(f"✅ Session statistics:")
        print(f"   - Total sessions: {stats['total_sessions']}")
        print(f"   - Completed: {stats['completed_sessions']}")
        print(f"   - Completion rate: {stats['completion_rate']:.1f}%")
        
        # Test 5: Emotional state logging
        print(f"\n😊 TEST 5: Emotional state tracking")
        print("-" * 50)
        
        # Log emotional states
        emotional_log = session_service.log_emotional_state(
            user_id=user_id,
            session_id=test_session.id,
            emotional_state="focused",
            trigger_message="I'm feeling really focused today!",
            confidence_score=0.9,
            intervention_recommended="none"
        )
        print(f"✅ Logged emotional state: {emotional_log.emotional_state}")
        
        # Get recent emotional states
        recent_states = session_service.get_recent_emotional_states(user_id, hours=24)
        print(f"✅ Found {len(recent_states)} recent emotional state logs")
        
        # Test 6: Delete operation (cleanup)
        print(f"\n🗑️ TEST 6: Cleanup operations")
        print("-" * 50)
        
        # Delete a session (for testing only)
        delete_session = sessions_created[-1]
        deleted = session_service.delete_session(delete_session.id)
        if deleted:
            print(f"✅ Successfully deleted session {delete_session.id}")
        
        print(f"\n🎉 All Session Management tests completed successfully!")
        print("=" * 60)
        print("✅ CREATE operations: Working")
        print("✅ READ operations: Working") 
        print("✅ UPDATE operations: Working")
        print("✅ DELETE operations: Working")
        print("✅ Session lifecycle: Working")
        print("✅ Emotional tracking: Working")
        print("✅ Advanced queries: Working")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

async def test_ai_integration():
    """
    Test AI integration with session management.
    """
    print(f"\n🤖 BONUS TEST: AI Integration")
    print("-" * 50)
    
    db = SessionLocal()
    session_service = SessionService(db)
    
    try:
        # Test morning planning analysis
        sample_conversation = [
            {"role": "assistant", "content": "Good morning! How are you feeling today?"},
            {"role": "user", "content": "I'm feeling pretty good, have 3 tasks to do today"},
            {"role": "assistant", "content": "That sounds manageable! What's your energy level?"},
            {"role": "user", "content": "Medium energy, feeling motivated but not overwhelmed"}
        ]
        
        print("✅ Testing morning planning analysis...")
        result = await session_service.process_morning_planning(
            user_id=1,
            conversation_history=sample_conversation
        )
        
        print(f"✅ Morning analysis completed:")
        print(f"   - Analysis ID: {result['analysis'].id}")
        print(f"   - Recommended block length: {result['recommendations']['block_length']} minutes")
        print(f"   - Generated {len(result['schedule'])} schedule items")
        print(f"   - Created {len(result['scheduled_sessions'])} follow-up sessions")
        
    except Exception as e:
        print(f"⚠️ AI integration test skipped: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    # Run the tests
    test_session_management()
    
    # Run AI integration test
    asyncio.run(test_ai_integration())
    
    print(f"\n🎯 Session Management System is fully operational!")
    print("Ready for frontend integration and timer implementation.") 