from typing import Dict, Any, Optional, List
import json
from datetime import datetime
from ai_service import ai_service
from database import SessionLocal
import sqlite3

class ChatService:
    """Chat service for text-based ADHD conversations"""
    
    def __init__(self):
        print("✅ Chat service initialized for text-based interactions")
        
    async def send_chat_message(
        self, 
        user_id: int,
        message: str,
        conversation_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return AI response
        
        Args:
            user_id: ID of the user sending the message
            message: User's text message
            conversation_context: Optional context for the conversation
            
        Returns:
            Dict with AI response and metadata
        """
        
        try:
            # Get user context and conversation history
            context = await self.get_conversation_context(user_id, conversation_context)
            
            # Process message with AI service
            ai_response = await ai_service.process_chat_conversation(
                user_message=message,
                user_context=context,
                session_type="chat_conversation"
            )
            
            # Store conversation in database
            await self.store_chat_interaction(user_id, message, ai_response)
            
            return {
                "success": True,
                "ai_response": ai_response,
                "context_updated": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Chat error for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "ai_response": "I'm having trouble processing your message right now. Could you please try again?"
            }
    
    async def get_conversation_context(
        self, 
        user_id: int, 
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get conversation context for user"""
        
        try:
            # Use SQLite directly for chat interactions
            conn = sqlite3.connect('./adhd_companion.db')
            cursor = conn.cursor()
            
            # Get recent chat history
            cursor.execute("""
                SELECT user_message, ai_response, created_at 
                FROM chat_interactions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 10
            """, (user_id,))
            
            recent_chats = cursor.fetchall()
            
            # Get user's current session state
            cursor.execute("""
                SELECT status_data, conversation_state, has_active_conversation
                FROM user_status 
                WHERE user_id = ?
            """, (user_id,))
            
            status_row = cursor.fetchone()
            conn.close()
            
            context = {
                "user_id": user_id,
                "recent_conversations": [
                    {
                        "user_message": row[0],
                        "ai_response": row[1],
                        "timestamp": row[2]
                    } for row in recent_chats
                ],
                "conversation_mode": "chat",
                "session_state": json.loads(status_row[0]) if status_row and status_row[0] else {},
                "conversation_state": status_row[1] if status_row else None,
                "has_active_conversation": bool(status_row[2]) if status_row else False
            }
            
            # Add additional context if provided
            if additional_context:
                context.update(additional_context)
            
            return context
            
        except Exception as e:
            print(f"Error getting conversation context for user {user_id}: {e}")
            return {
                "user_id": user_id,
                "conversation_mode": "chat",
                "error": "Could not load conversation context"
            }
    
    async def store_chat_interaction(
        self, 
        user_id: int, 
        user_message: str, 
        ai_response: str
    ) -> bool:
        """Store chat interaction in database"""
        
        try:
            conn = sqlite3.connect('./adhd_companion.db')
            cursor = conn.cursor()
            
            # Create chat_interactions table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_message TEXT NOT NULL,
                    ai_response TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Insert the interaction
            cursor.execute("""
                INSERT INTO chat_interactions 
                (user_id, user_message, ai_response, metadata)
                VALUES (?, ?, ?, ?)
            """, (
                user_id, 
                user_message, 
                ai_response,
                json.dumps({"interaction_type": "chat", "timestamp": datetime.now().isoformat()})
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error storing chat interaction for user {user_id}: {e}")
            return False
    
    async def get_chat_history(
        self, 
        user_id: int, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get chat history for user"""
        
        try:
            conn = sqlite3.connect('./adhd_companion.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_message, ai_response, created_at, metadata
                FROM chat_interactions 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "user_message": row[0],
                    "ai_response": row[1],
                    "timestamp": row[2],
                    "metadata": json.loads(row[3]) if row[3] else {}
                } for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting chat history for user {user_id}: {e}")
            return []
    
    async def clear_chat_history(self, user_id: int) -> bool:
        """Clear chat history for user"""
        
        try:
            conn = sqlite3.connect('./adhd_companion.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM chat_interactions 
                WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error clearing chat history for user {user_id}: {e}")
            return False

# Global chat service instance
chat_service = ChatService() 