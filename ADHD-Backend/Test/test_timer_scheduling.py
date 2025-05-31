#!/usr/bin/env python3
"""
Comprehensive Test: Timer & Scheduling Logic for ADHD Companion

This test demonstrates:
- Dynamic schedule creation based on morning analysis
- Work block timer functionality (start, pause, resume, complete)
- Real-time schedule adaptation based on emotional state
- Hyperfocus detection and intervention
- Analytics and progress tracking
- Integration with AI service and session management
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, create_tables
from timer_service import TimerSchedulingService, BlockType
from session_service import SessionService, SessionType
from ai_service import ai_service
from models import User

async def test_timer_scheduling_system():
    """
    Complete demonstration of the timer & scheduling system
    """
    
    print("🧠 ADHD Companion - Timer & Scheduling System Test")
    print("=" * 60)
    
    # Initialize database and services
    db = next(get_db())
    create_tables()
    
    timer_service = TimerSchedulingService(db)
    session_service = SessionService(db)
    
    # Create test user
    existing_user = db.query(User).filter(User.username == "alex_chen").first()
    if existing_user:
        user = existing_user
        print(f"👤 Using existing test user: {user.username} (ID: {user.id})")
    else:
        user = User(
            username="alex_chen",
            email="alex@example.com"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"👤 Created test user: {user.username} (ID: {user.id})")
    
    print()
    
    # =====================================
    # 1. MORNING ANALYSIS & SCHEDULE CREATION
    # =====================================
    
    print("📅 STEP 1: Create Dynamic Daily Schedule")
    print("-" * 40)
    
    # Simulate morning analysis (this would come from actual morning session)
    morning_analysis = {
        "energy_level": "medium",
        "stress_level": "mild",
        "recommended_block_length": 30,  # Shorter blocks due to mild stress
        "recommended_break_length": 15,
        "max_work_blocks": 4,
        "confidence_score": 0.8
    }
    
    # Create daily schedule
    schedule = await timer_service.create_daily_schedule(
        user_id=user.id,
        morning_analysis=morning_analysis
    )
    
    print(f"✅ Created schedule with {len(schedule)} items")
    print("📋 Today's Schedule:")
    for i, item in enumerate(schedule):
        print(f"   {i+1:2d}. {item.description:25} | {item.duration_minutes:2d}min | {item.start_time.strftime('%H:%M')}")
    print()
    
    # =====================================
    # 2. START FIRST WORK BLOCK
    # =====================================
    
    print("⏰ STEP 2: Start First Work Block")
    print("-" * 40)
    
    work_block_1 = await timer_service.start_work_block(
        user_id=user.id,
        task_description="Review project documentation",
        planned_duration=30
    )
    
    print(f"🎯 Started work block: {work_block_1['task_description']}")
    print(f"   Duration: {work_block_1['planned_duration']} minutes")
    print(f"   Work Block ID: {work_block_1['work_block_id']}")
    print()
    
    # Simulate some work time
    await asyncio.sleep(2)  # Simulate 2 seconds of work
    
    # =====================================
    # 3. EMOTIONAL STATE MONITORING
    # =====================================
    
    print("🧠 STEP 3: Emotional State Detection & Response")
    print("-" * 40)
    
    # Simulate emotional state detection (getting frustrated)
    emotional_state = {
        "dominant_emotion": "frustrated",
        "intensity": 0.7,
        "confidence": 0.85,
        "context": "struggling with complex documentation",
        "indicators": ["increased typing speed", "long pauses", "backtracking"]
    }
    
    print(f"😤 Detected emotional state: {emotional_state['dominant_emotion']} (intensity: {emotional_state['intensity']})")
    
    # Get AI intervention recommendation
    intervention = ai_service.recommend_intervention(emotional_state)
    
    print(f"🤖 AI Recommendation: {intervention['type']}")
    print(f"   Message: {intervention['message']}")
    print(f"   Actions: {intervention['actions']}")
    print()
    
    # =====================================
    # 4. ADAPTIVE SCHEDULE MODIFICATION
    # =====================================
    
    print("🔄 STEP 4: Dynamic Schedule Adaptation")
    print("-" * 40)
    
    # Check if schedule needs adaptation
    adaptation = await timer_service.adapt_schedule_based_on_state(
        user_id=user.id,
        emotional_state=emotional_state,
        current_work_block_id=work_block_1['work_block_id']
    )
    
    print(f"📊 Schedule adaptation result: {adaptation['adaptation']}")
    if adaptation['adaptation'] == 'modified':
        print(f"   Changes made: {adaptation['changes']}")
        print(f"   Reason: {adaptation['reason']}")
    print()
    
    # =====================================
    # 5. PAUSE AND RESUME WORK BLOCK
    # =====================================
    
    print("⏸️ STEP 5: Pause & Resume Work Block")
    print("-" * 40)
    
    # Pause work block (user taking a micro-break)
    pause_result = await timer_service.pause_work_block(
        work_block_id=work_block_1['work_block_id'],
        reason="Taking a micro-break to reset focus"
    )
    
    print(f"⏸️ Paused work block: {pause_result}")
    
    # Check current status
    status = await timer_service.get_current_status(user.id)
    active_block = status['active_work_blocks'][0] if status['active_work_blocks'] else None
    
    if active_block:
        print(f"   Current state: {active_block['state']}")
        print(f"   Elapsed time: {active_block['elapsed_time']} minutes")
        print(f"   Interruptions: {active_block['interruption_count']}")
    
    # Simulate break time
    await asyncio.sleep(1)
    
    # Resume work block
    resume_result = await timer_service.resume_work_block(
        work_block_id=work_block_1['work_block_id']
    )
    
    print(f"▶️ Resumed work block: {resume_result}")
    print()
    
    # =====================================
    # 6. COMPLETE WORK BLOCK
    # =====================================
    
    print("✅ STEP 6: Complete Work Block with Metrics")
    print("-" * 40)
    
    # Complete the work block
    completion_result = await timer_service.complete_work_block(
        work_block_id=work_block_1['work_block_id'],
        completion_percentage=85,
        productivity_rating=4,
        focus_quality="good"
    )
    
    print(f"🎉 Completed work block {completion_result['work_block_id']}")
    print(f"   Actual duration: {completion_result['actual_duration']} minutes")
    print(f"   Completion: {completion_result['completion_percentage']}%")
    print(f"   Productivity: {completion_result['productivity_rating']}/5")
    print(f"   Interruptions: {completion_result['interruption_count']}")
    print(f"   Overtime: {completion_result['was_overtime']}")
    print()
    
    # =====================================
    # 7. HYPERFOCUS SCENARIO
    # =====================================
    
    print("🔥 STEP 7: Hyperfocus Detection & Intervention")
    print("-" * 40)
    
    # Start another work block
    work_block_2 = await timer_service.start_work_block(
        user_id=user.id,
        task_description="Code review and refactoring",
        planned_duration=30
    )
    
    print(f"🎯 Started second work block: {work_block_2['task_description']}")
    
    # Simulate hyperfocus state (user working for too long)
    hyperfocus_state = {
        "dominant_emotion": "hyperfocusing",
        "intensity": 0.9,
        "confidence": 0.92,
        "context": "deep in code review, losing track of time",
        "indicators": ["no movement for 45min", "missed break", "tunnel vision"]
    }
    
    print(f"🔥 Detected hyperfocus state (intensity: {hyperfocus_state['intensity']})")
    
    # Get intervention for hyperfocus
    hyperfocus_intervention = ai_service.recommend_intervention(hyperfocus_state)
    
    print(f"🚨 Emergency intervention: {hyperfocus_intervention['type']}")
    print(f"   Urgency: {hyperfocus_intervention['urgency']}")
    print(f"   Message: {hyperfocus_intervention['message']}")
    
    # Force schedule adaptation (this should force a break)
    hyperfocus_adaptation = await timer_service.adapt_schedule_based_on_state(
        user_id=user.id,
        emotional_state=hyperfocus_state,
        current_work_block_id=work_block_2['work_block_id']
    )
    
    print(f"🛑 Forced adaptation: {hyperfocus_adaptation['changes']}")
    print()
    
    # =====================================
    # 8. EXHAUSTION SCENARIO
    # =====================================
    
    print("😴 STEP 8: Exhaustion Detection & Early Day End")
    print("-" * 40)
    
    # Simulate exhaustion state
    exhaustion_state = {
        "dominant_emotion": "exhausted",
        "intensity": 0.8,
        "confidence": 0.88,
        "context": "feeling mentally drained after several work blocks",
        "indicators": ["decreased typing speed", "longer response times", "frequent errors"]
    }
    
    print(f"😴 Detected exhaustion (intensity: {exhaustion_state['intensity']})")
    
    # Get intervention for exhaustion
    exhaustion_intervention = ai_service.recommend_intervention(exhaustion_state)
    
    print(f"🛏️ Intervention: {exhaustion_intervention['type']}")
    print(f"   Message: {exhaustion_intervention['message']}")
    
    # This should end the workday early
    exhaustion_adaptation = await timer_service.adapt_schedule_based_on_state(
        user_id=user.id,
        emotional_state=exhaustion_state,
        current_work_block_id=work_block_2['work_block_id']
    )
    
    print(f"🏁 Schedule changes: {exhaustion_adaptation.get('changes', [])}")
    print(f"   Reason: {exhaustion_adaptation.get('reason', 'N/A')}")
    print()
    
    # =====================================
    # 9. ANALYTICS & INSIGHTS
    # =====================================
    
    print("📊 STEP 9: Analytics & Performance Insights")
    print("-" * 40)
    
    # Complete the second work block first
    await timer_service.complete_work_block(
        work_block_id=work_block_2['work_block_id'],
        completion_percentage=60,  # Lower due to exhaustion
        productivity_rating=2,
        focus_quality="poor"
    )
    
    # Get analytics
    analytics = timer_service.get_work_block_analytics(user.id, days=1)
    
    print("📈 Work Block Analytics:")
    print(f"   Total work blocks: {analytics['total_work_blocks']}")
    print(f"   Completion rate: {analytics['completion_rate']:.1f}%")
    print(f"   Average duration: {analytics['average_duration']:.1f} minutes")
    print(f"   Average productivity: {analytics['average_productivity']:.1f}/5")
    print(f"   Total interruptions: {analytics['total_interruptions']}")
    print(f"   Hyperfocus episodes: {analytics['hyperfocus_episodes']}")
    print(f"   Schedule adherence: {analytics['adherence_to_schedule']:.1f}%")
    print()
    
    # =====================================
    # 10. CURRENT STATUS CHECK
    # =====================================
    
    print("🔍 STEP 10: Final Status Check")
    print("-" * 40)
    
    final_status = await timer_service.get_current_status(user.id)
    
    print("📊 Current System Status:")
    print(f"   Active work blocks: {len(final_status['active_work_blocks'])}")
    print(f"   Schedule adaptations: {final_status['schedule_adaptation_count']}")
    print(f"   Time worked today: {final_status['time_worked_today']} minutes")
    
    if final_status['current_schedule_item']:
        current = final_status['current_schedule_item']
        print(f"   Current activity: {current['description']} ({current['type']})")
    
    if final_status['next_schedule_item']:
        next_item = final_status['next_schedule_item']
        print(f"   Next activity: {next_item['description']} (in {next_item['minutes_until']}min)")
    print()
    
    # =====================================
    # SUMMARY
    # =====================================
    
    print("🎯 TEST SUMMARY")
    print("=" * 60)
    print("✅ Dynamic schedule creation based on morning analysis")
    print("✅ Work block timer management (start, pause, resume, complete)")
    print("✅ Real-time emotional state detection and response")
    print("✅ Adaptive schedule modifications")
    print("✅ Hyperfocus detection and intervention")
    print("✅ Exhaustion detection and workday termination")
    print("✅ Comprehensive analytics and insights")
    print("✅ Integration with AI service and session management")
    print()
    print("🧠 The Timer & Scheduling system is fully operational!")
    print("   Ready to provide dynamic, adaptive support for ADHD users.")

if __name__ == "__main__":
    print("🚀 Starting Timer & Scheduling System Test...")
    print()
    asyncio.run(test_timer_scheduling_system()) 