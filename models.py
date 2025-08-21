#!/usr/bin/env python3
"""
Database Models for Finance Chatbot
PostgreSQL schema with SQLAlchemy ORM
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    """User table for chatbot users"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship to chat sessions
    chat_sessions = relationship("ChatSession", back_populates="user")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class ChatSession(Base):
    """Chat session table"""
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_title = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship to messages
    messages = relationship("ChatMessage", back_populates="session")
    user = relationship("User", back_populates="chat_sessions")
    
    def __repr__(self):
        return f"<ChatSession(title='{self.session_title}', user_id={self.user_id})>"

class ChatMessage(Base):
    """Individual chat messages"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, default=0)
    
    # Relationship to session
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(role='{self.role}', content='{self.content[:50]}...')>"

class UserPreference(Base):
    """User preferences and settings"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    preference_key = Column(String(100), nullable=False)
    preference_value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<UserPreference(key='{self.preference_key}', value='{self.preference_value}')>"

# Database connection setup
def get_database_url():
    """Get database URL from environment or use default"""
    return os.getenv('DATABASE_URL', 'postgresql://localhost/finance_chatbot')

def create_database_engine():
    """Create database engine"""
    database_url = get_database_url()
    return create_engine(database_url)

def create_tables():
    """Create all tables"""
    engine = create_database_engine()
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully")

def get_session():
    """Get database session"""
    engine = create_database_engine()
    Session = sessionmaker(bind=engine)
    return Session()

# Sample data functions
def create_sample_user():
    """Create a sample user for testing"""
    session = get_session()
    
    # Check if user already exists
    existing_user = session.query(User).filter_by(username='test_user').first()
    if existing_user:
        print("✅ Sample user already exists")
        return existing_user
    
    # Create new user
    user = User(
        username='test_user',
        email='test@example.com'
    )
    session.add(user)
    session.commit()
    print("✅ Sample user created successfully")
    return user

def create_sample_chat_session(user_id):
    """Create a sample chat session"""
    session = get_session()
    
    chat_session = ChatSession(
        user_id=user_id,
        session_title='Sample Finance Discussion'
    )
    session.add(chat_session)
    session.commit()
    print("✅ Sample chat session created")
    return chat_session

def add_sample_messages(session_id):
    """Add sample messages to a chat session"""
    db_session = get_session()
    
    messages = [
        ChatMessage(
            session_id=session_id,
            role='user',
            content='What are the best investment options for beginners?',
            tokens_used=15
        ),
        ChatMessage(
            session_id=session_id,
            role='assistant',
            content='For beginners, I recommend starting with index funds and ETFs. They provide diversification and are less risky than individual stocks.',
            tokens_used=25
        ),
        ChatMessage(
            session_id=session_id,
            role='user',
            content='How much should I invest initially?',
            tokens_used=10
        ),
        ChatMessage(
            session_id=session_id,
            role='assistant',
            content='Start with what you can afford to lose. Many experts suggest 10-15% of your income. Even $100-500 monthly can grow significantly over time.',
            tokens_used=35
        )
    ]
    
    for message in messages:
        db_session.add(message)
    
    db_session.commit()
    print("✅ Sample messages added successfully")

if __name__ == "__main__":
    # Create tables and sample data
    print("🗄️ Setting up database...")
    create_tables()
    
    print("👤 Creating sample user...")
    user = create_sample_user()
    
    print("💬 Creating sample chat session...")
    chat_session = create_sample_chat_session(user.id)
    
    print("📝 Adding sample messages...")
    add_sample_messages(chat_session.id)
    
    print("✅ Database setup complete!")
