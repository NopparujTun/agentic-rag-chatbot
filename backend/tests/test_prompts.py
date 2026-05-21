import pytest
from app.rag import prompts
from langchain_core.messages import SystemMessage

def test_get_registrar_assistant_prompt():
    prompt = prompts.get_registrar_assistant_prompt()
    assert isinstance(prompt, SystemMessage)
    assert "คุณคือ AI ผู้ช่วยเชี่ยวชาญด้าน" in prompt.content
    assert "search_knowledge_base" in prompt.content
