from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Optional
import json
from pydantic import BaseModel
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .database import get_db, init_db
from .models import ChatSession, Message
from .services.ai_service import ai_service
from .services.search_service import search_service
from .config import settings
from sqlalchemy import select

app = FastAPI(title="Personal Knowledge Assistant")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:3000", "http://localhost"],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.on_event("startup")
async def startup_event():
    """
    在应用启动时初始化数据库
    """
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    session_id: Optional[int] = None

@app.get("/models")
async def list_models():
    """Get list of available models from SiliconFlow API"""
    logger.info("Getting available models")
    return await ai_service.list_models()

@app.post("/chat/")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"[Step 1] Received chat request: {request}")
    
    # Create new session if none exists
    if not request.session_id:
        new_session = ChatSession(title=request.message[:50])  # Use first 50 chars as title
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        request.session_id = new_session.id
        logger.info(f"[Step 2] Created new session with ID: {request.session_id}")

    # Perform web search
    logger.info("[Step 3] Starting web search...")
    search_results = await search_service.search(request.message)
    logger.info(f"[Step 4] Completed web search, got {len(search_results)} results")
    
    # Store user message
    user_message = Message(
        session_id=request.session_id,
        role="user",
        content=request.message,
        search_results=json.dumps(search_results)
    )
    db.add(user_message)
    logger.info("[Step 5] Stored user message")
    
    # Prepare context for AI
    context = f"Web search results:\n"
    # 只使用前3条最相关的搜索结果
    for i, result in enumerate(search_results[:3]):
        context += f"{i+1}. {result['title']}\n{result['snippet']}\n\n"
    
    # Get AI response
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. Use the provided web search results to help answer questions accurately. Keep your response concise and focused."},
        {"role": "user", "content": f"Context: {context}\n\nQuestion: {request.message}"}
    ]
    
    try:
        logger.info(f"[Step 6] Starting AI request using model: {request.model or settings.DEFAULT_MODEL}")
        logger.info(f"[Step 6.1] Context length: {len(context)} chars")
        ai_response = await ai_service.get_ai_response(messages, request.model)
        logger.info("[Step 7] Received AI response")
        
        # Store AI response
        assistant_message = Message(
            session_id=request.session_id,
            role="assistant",
            content=ai_response,
            ai_model_response=json.dumps({
                "response": ai_response,
                "model": request.model or settings.DEFAULT_MODEL
            })
        )
        db.add(assistant_message)
        
        await db.commit()
        logger.info("[Step 8] Stored AI response in database")
        
        return {
            "session_id": request.session_id,
            "response": ai_response,
            "search_results": search_results,
            "model": request.model or settings.DEFAULT_MODEL
        }
    except HTTPException as e:
        logger.error(f"[Error] HTTP error in step 6-8: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"[Error] General error in step 6-8: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/sessions/")
async def get_sessions(db: AsyncSession = Depends(get_db)):
    logger.info("Getting all sessions")
    result = await db.execute(select(ChatSession).order_by(ChatSession.created_at.desc()))
    sessions = result.scalars().all()
    return sessions

@app.get("/sessions/{session_id}/messages/")
async def get_session_messages(session_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"Getting messages for session {session_id}")
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    return messages 