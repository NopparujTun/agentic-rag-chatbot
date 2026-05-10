from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    """Data model for a chat request."""
    query: str
    chat_history: str = ""

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    organization_name: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    organization_id: str
    created_at: datetime

    class Config:
        from_attributes = True
