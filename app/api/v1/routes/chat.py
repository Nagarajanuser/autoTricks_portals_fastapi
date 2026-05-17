from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.chat_service import query_rag_chatbot

router = APIRouter()

from typing import List, Optional

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = None

class ChatResponse(BaseModel):
    reply: str

@router.post("/message", response_model=ChatResponse)
async def chat_with_hr_bot(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    reply = query_rag_chatbot(request.message, request.history)
    return ChatResponse(reply=reply)
