from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    title = Column(String(255))

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"))
    role = Column(String(50))  # user, assistant, or system
    content = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional fields for search results and AI responses
    search_results = Column(Text, nullable=True)
    ai_model_response = Column(Text, nullable=True) 