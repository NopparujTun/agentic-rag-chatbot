from pydantic import BaseModel

class ChatRequest(BaseModel):
    """Data model for a chat request."""
    query: str
    chat_history: str = ""
