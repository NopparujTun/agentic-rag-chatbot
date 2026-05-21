import pytest
from unittest.mock import patch, MagicMock
from app.services import chat_service
from langchain_core.documents import Document
from langchain_core.agents import AgentAction

@patch("app.services.chat_service.generate_answer")
def test_process_chat_success(mock_generate_answer):
    mock_generate_answer.return_value = (
        "Answer",
        [Document(page_content="doc1", metadata={"source": "test.pdf"})],
        [(AgentAction(tool="search", tool_input={"q": "test"}, log=""), "obs1")]
    )
    
    mock_vs = MagicMock()
    mock_reranker = MagicMock()
    
    result = chat_service.process_chat("query", "history", mock_vs, mock_reranker)
    
    assert result["answer"] == "Answer"
    assert len(result["sources"]) == 1
    assert result["sources"][0]["content"] == "doc1"
    assert result["sources"][0]["metadata"] == {"source": "test.pdf"}
    
    assert len(result["steps"]) == 1
    assert result["steps"][0]["tool"] == "search"
    assert result["steps"][0]["tool_input"] == {"q": "test"}
    assert result["steps"][0]["observation"] == "obs1"
    
    assert "response_time_seconds" in result

def test_process_chat_no_vs():
    with pytest.raises(ValueError):
        chat_service.process_chat("query", "history", None, None)
