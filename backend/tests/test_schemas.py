import pytest
from app.models.schemas import ChatRequest
from pydantic import ValidationError

def test_chat_request_valid():
    request = ChatRequest(query="Hello")
    assert request.query == "Hello"
    assert request.chat_history == ""

def test_chat_request_invalid():
    with pytest.raises(ValidationError):
        ChatRequest() # Missing query
