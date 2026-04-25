from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    scenario: Optional[Dict[str, Any]] = None
    session_id: str

# In-memory store of chat sessions (for demo; use Redis in production)
chat_sessions: Dict[str, Any] = {}

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())
    
    # Get or create chatbot instance for this session
    if session_id not in chat_sessions:
        from app.services.chat_service import ChatService
        chat_sessions[session_id] = ChatService()
    
    service = chat_sessions[session_id]
    response, scenario = service.process_message(request.message)
    return ChatResponse(response=response, scenario=scenario, session_id=session_id)