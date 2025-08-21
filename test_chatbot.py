#!/usr/bin/env python3
"""
Test Finance Chatbot - Database Integration Test
Tests database functionality without requiring API keys
"""

import os
from models import User, ChatSession, ChatMessage, get_session, create_tables
from datetime import datetime

class TestFinanceChatbot:
    def __init__(self):
        """Initialize test chatbot with database integration"""
        # Initialize database
        self.setup_database()
        
        print("✅ Test chatbot initialized successfully!")
    
    def setup_database(self):
        """Setup database tables if they don't exist"""
        try:
            create_tables()
            print("✅ Database setup completed")
        except Exception as e:
            print(f"⚠️ Database setup warning: {e}")
    
    def get_or_create_user(self, username, email=None):
        """Get existing user or create new one"""
        session = get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                user = User(username=username, email=email)
                session.add(user)
                session.commit()
                print(f"✅ Created new user: {username}")
            else:
                print(f"✅ Found existing user: {username}")
            return user
        except Exception as e:
            print(f"❌ Error managing user: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def create_chat_session(self, user_id, title="New Chat"):
        """Create a new chat session"""
        session = get_session()
        try:
            chat_session = ChatSession(
                user_id=user_id,
                session_title=title
            )
            session.add(chat_session)
            session.commit()
            session.refresh(chat_session)  # Refresh to get the ID
            print(f"✅ Created chat session: {title}")
            return chat_session
        except Exception as e:
            print(f"❌ Error creating chat session: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def save_message(self, session_id, role, content, tokens_used=0):
        """Save a message to the database"""
        session = get_session()
        try:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                tokens_used=tokens_used
            )
            session.add(message)
            session.commit()
            print(f"✅ Saved {role} message: {content[:50]}...")
            return message
        except Exception as e:
            print(f"❌ Error saving message: {e}")
            session.rollback()
            return None
        finally:
            session.close()
    
    def get_chat_history(self, session_id, limit=10):
        """Get chat history for a session"""
        session = get_session()
        try:
            messages = session.query(ChatMessage)\
                .filter_by(session_id=session_id)\
                .order_by(ChatMessage.timestamp.desc())\
                .limit(limit)\
                .all()
            return list(reversed(messages))  # Return in chronological order
        except Exception as e:
            print(f"❌ Error getting chat history: {e}")
            return []
        finally:
            session.close()
    
    def get_user_sessions(self, user_id):
        """Get all chat sessions for a user"""
        session = get_session()
        try:
            sessions = session.query(ChatSession)\
                .filter_by(user_id=user_id, is_active=True)\
                .order_by(ChatSession.updated_at.desc())\
                .all()
            return sessions
        except Exception as e:
            print(f"❌ Error getting user sessions: {e}")
            return []
        finally:
            session.close()
    
    def simulate_chat(self, message, user_id=None, session_id=None, username="test_user"):
        """Simulate chat without API calls"""
        try:
            # Get or create user if user_id provided
            user = None
            if user_id:
                session = get_session()
                user = session.query(User).filter_by(id=user_id).first()
                session.close()
            elif username != "anonymous":
                user = self.get_or_create_user(username)
                user_id = user.id if user else None
            
            # Create session if not provided
            if not session_id and user_id:
                session_title = f"Chat about {message[:50]}..."
                chat_session = self.create_chat_session(user_id, session_title)
                session_id = chat_session.id if chat_session else None
                
                # If session creation failed, return error
                if not session_id:
                    return {
                        "response": "I apologize, but I encountered an error creating a chat session.",
                        "error": "Failed to create chat session"
                    }
            
            # Save user message
            if session_id:
                self.save_message(session_id, "user", message)
            
            # Simulate AI response
            ai_response = f"This is a simulated response to: '{message}'. In a real implementation, this would be generated by OpenAI's API."
            
            # Save assistant message
            if session_id:
                self.save_message(session_id, "assistant", ai_response, tokens_used=25)
            
            return {
                "response": ai_response,
                "session_id": session_id,
                "user_id": user_id,
                "tokens_used": 25,
                "context_used": False
            }
            
        except Exception as e:
            print(f"❌ Error in simulated chat: {e}")
            return {
                "response": "I apologize, but I encountered an error. Please try again.",
                "error": str(e)
            }
    
    def get_user_stats(self, user_id):
        """Get user statistics"""
        session = get_session()
        try:
            # Get total sessions
            total_sessions = session.query(ChatSession)\
                .filter_by(user_id=user_id)\
                .count()
            
            # Get total messages
            total_messages = session.query(ChatMessage)\
                .join(ChatSession)\
                .filter(ChatSession.user_id == user_id)\
                .count()
            
            # Get total tokens used
            total_tokens = session.query(ChatMessage.tokens_used)\
                .join(ChatSession)\
                .filter(ChatSession.user_id == user_id)\
                .all()
            total_tokens = sum([t[0] for t in total_tokens])
            
            return {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "total_tokens": total_tokens
            }
        except Exception as e:
            print(f"❌ Error getting user stats: {e}")
            return {}
        finally:
            session.close()
    
    def display_chat_history(self, session_id):
        """Display chat history for a session"""
        messages = self.get_chat_history(session_id)
        if not messages:
            print("📝 No messages found for this session")
            return
        
        print(f"\n📝 Chat History (Session {session_id}):")
        print("=" * 60)
        for i, msg in enumerate(messages, 1):
            role_icon = "👤" if msg.role == "user" else "🤖"
            print(f"{i}. {role_icon} {msg.role.upper()}: {msg.content}")
            print(f"   📅 {msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            if msg.tokens_used > 0:
                print(f"   🔢 Tokens: {msg.tokens_used}")
            print()

# Test the enhanced chatbot
if __name__ == "__main__":
    print("🧪 Testing Enhanced Finance Chatbot with Database...")
    
    # Initialize chatbot
    chatbot = TestFinanceChatbot()
    
    # Test with database integration
    test_user = chatbot.get_or_create_user("test_user", "test@example.com")
    
    if test_user:
        # Get fresh user data from database
        session = get_session()
        user = session.query(User).filter_by(id=test_user.id).first()
        session.close()
        
        if user:
            print(f"\n👤 User ID: {user.id}")
            print(f"📧 Email: {user.email}")
        
        # Test chat functionality
        print("\n💬 Testing chat functionality...")
        response1 = chatbot.simulate_chat(
            "What are the best investment options for beginners?",
            user_id=user.id,
            username="test_user"
        )
        
        print(f"🤖 Response: {response1['response']}")
        print(f"📊 Session ID: {response1['session_id']}")
        print(f"🔢 Tokens Used: {response1['tokens_used']}")
        
        # Test another message in the same session
        print("\n💬 Testing second message...")
        response2 = chatbot.simulate_chat(
            "How much should I invest initially?",
            user_id=user.id,
            session_id=response1['session_id']
        )
        
        print(f"🤖 Response: {response2['response']}")
        
        # Display chat history
        chatbot.display_chat_history(response1['session_id'])
        
        # Get user stats
        stats = chatbot.get_user_stats(user.id)
        print(f"📈 User Stats: {stats}")
        
        # Test user sessions
        sessions = chatbot.get_user_sessions(user.id)
        print(f"\n📋 User Sessions: {len(sessions)}")
        for session in sessions:
            print(f"   - Session {session.id}: {session.session_title}")
    
    print("\n✅ Enhanced chatbot test completed!")
