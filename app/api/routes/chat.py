# app/api/routes/chat.py

from fastapi import APIRouter, Depends, HTTPException
from app.services.chat import ChatService
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.logging_config import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends()
):
    try:
        response = await chat_service.generate_response(chat_request)
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))