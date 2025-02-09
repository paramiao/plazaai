from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
import logging

from ..database import get_db
from ..models import ChatSession, Message
from ..services.ai_service import ai_service
from ..services.search_service import search_service

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]

@router.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db)
) -> ChatCompletionResponse:
    """
    处理聊天完成请求，格式兼容 ChatGPT API
    """
    try:
        # 获取用户最新的消息
        user_message = request.messages[-1].content
        
        # 创建或获取会话
        session_result = await db.execute(
            "SELECT id FROM chat_sessions ORDER BY created_at DESC LIMIT 1"
        )
        session_id = session_result.scalar()
        
        if not session_id:
            new_session = ChatSession(title=user_message[:50])
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            session_id = new_session.id

        # 执行网络搜索
        search_results = await search_service.search(user_message)
        
        # 存储用户消息
        user_msg = Message(
            session_id=session_id,
            role="user",
            content=user_message,
            search_results=json.dumps(search_results)
        )
        db.add(user_msg)
        
        # 准备上下文
        context = "Web search results:\n"
        for i, result in enumerate(search_results[:3]):
            context += f"{i+1}. {result['title']}\n{result['snippet']}\n\n"
        
        # 准备消息列表
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Use the provided web search results to help answer questions accurately. Keep your response concise and focused."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {user_message}"}
        ]
        
        # 获取 AI 响应
        ai_response = await ai_service.get_ai_response(messages, request.model)
        
        # 存储助手响应
        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=ai_response,
            ai_model_response=json.dumps({
                "response": ai_response,
                "model": request.model,
                "search_results": search_results
            })
        )
        db.add(assistant_msg)
        await db.commit()
        
        # 返回 ChatGPT API 兼容的响应格式
        import time
        response = ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model or "deepseek-chat",
            choices=[{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": ai_response
                },
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": len(str(messages)),
                "completion_tokens": len(ai_response),
                "total_tokens": len(str(messages)) + len(ai_response)
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        ) 