"""
ADHD Companion Test Suite

This test suite covers all major components of the ADHD Companion backend:
- Groq API integration (Text Generation, STT, TTS)
- Dynamic timer system
- Session management
- Real-time adaptations
"""

# Test modules
from .test_full_groq_integration import *
from .test_dynamic_system import *
from .test_session_management import *
from .test_timer_scheduling import * 