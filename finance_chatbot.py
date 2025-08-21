#!/usr/bin/env python3
"""
Finance Assistant Chatbot with Database Integration
Enhanced with user management and chat history persistence
"""

import os
import json
import openai
from pinecone import Pinecone
from models import User, ChatSession, ChatMessage, get_session, create_tables
from datetime import datetime
from config import config

class FinanceChatbot:
    def __init__(self):
        """Initialize the finance chatbot with database integration"""
        # Initialize OpenAI
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize Pinecone
        self.pinecone = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        self.index = self.pinecone.Index(config.PINECONE_INDEX_NAME)
        
        # Initialize database
        self.setup_database()
        
        # Default system message
        self.system_message = """You are a knowledgeable finance assistant specializing in:
        - Investment advice and strategies
        - Personal finance management
        - Market analysis and trends
        - Retirement planning
        - Tax optimization
        - Risk management
        
        Provide clear, practical advice while being mindful of regulatory compliance.
        Always recommend consulting with qualified financial professionals for specific advice."""
    
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
    
    def search_knowledge_base(self, query, top_k=3):
        """Search the Pinecone knowledge base"""
        try:
            # Create embedding for the query
            response = self.openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
            query_embedding = response.data[0].embedding
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            return results.matches
        except Exception as e:
            print(f"❌ Error searching knowledge base: {e}")
            return []
    
    def chat(self, message, user_id=None, session_id=None, username="anonymous"):
        """Enhanced chat method with database integration"""
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
            
            # Save user message
            if session_id:
                self.save_message(session_id, "user", message)
            
            # Get chat history for context
            chat_history = []
            if session_id:
                chat_history = self.get_chat_history(session_id, limit=5)
            
            # Search knowledge base
            knowledge_results = self.search_knowledge_base(message)
            context = ""
            if knowledge_results:
                context = "\n\nRelevant information:\n" + "\n".join([
                    f"- {match.metadata.get('text', '')}" 
                    for match in knowledge_results
                ])
            
            # Prepare messages for OpenAI
            messages = [{"role": "system", "content": self.system_message}]
            
            # Add chat history
            for msg in chat_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add current message with context
            messages.append({
                "role": "user", 
                "content": f"{message}{context}"
            })
            
            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            
            assistant_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Save assistant message
            if session_id:
                self.save_message(session_id, "assistant", assistant_message, tokens_used)
            
            return {
                "response": assistant_message,
                "session_id": session_id,
                "user_id": user_id,
                "tokens_used": tokens_used,
                "context_used": len(knowledge_results) > 0
            }
            
        except Exception as e:
            print(f"❌ Error in chat: {e}")
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

# Test the enhanced chatbot
if __name__ == "__main__":
    print("🧪 Testing enhanced finance chatbot...")
    
    # Initialize chatbot
    chatbot = FinanceChatbot()
    
    # Test with database integration
    test_user = chatbot.get_or_create_user("test_user", "test@example.com")
    
    if test_user:
        # Test chat functionality
        response = chatbot.chat(
            "What are the best investment options for beginners?",
            user_id=test_user.id,
            username="test_user"
        )
        
        print(f"🤖 Response: {response['response']}")
        print(f"📊 Session ID: {response['session_id']}")
        print(f"🔢 Tokens Used: {response['tokens_used']}")
        
        # Get user stats
        stats = chatbot.get_user_stats(test_user.id)
        print(f"📈 User Stats: {stats}")
    
    print("✅ Enhanced chatbot test completed!")
