from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

# Pydantic models for API requests and responses
class ChatMessage(BaseModel):
    content: str
    from_user: bool = True
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    model_name: Optional[str] = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    model_used: str
    timestamp: datetime
