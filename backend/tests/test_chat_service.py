import pytest
from unittest.mock import patch, MagicMock
from app.services import chat_service
from langchain_core.documents import Document
from langchain_core.agents import AgentAction


@patch("app.services.chat_service.RAGAgent")
@patch("app.services.chat_service.PineconeRetriever")
def test_answer_query_success(mock_retriever, mock_agent_cls):
    mock_agent = MagicMock()
    mock_agent.generate.return_value = (
        "Answer",
        [Document(page_content="doc1", metadata={"source": "test.pdf"})],
        [(AgentAction(tool="search", tool_input={"q": "test"}, log=""), "obs1")],
    )
    mock_agent_cls.return_value = mock_agent

    result = chat_service.answer_query("query", "history", MagicMock(), MagicMock())

    assert result["answer"] == "Answer"
    assert len(result["sources"]) == 1
    assert result["sources"][0]["content"] == "doc1"
    assert result["sources"][0]["metadata"] == {"source": "test.pdf"}

    assert len(result["steps"]) == 1
    assert result["steps"][0]["tool"] == "search"
    assert result["steps"][0]["tool_input"] == {"q": "test"}
    assert result["steps"][0]["observation"] == "obs1"

    assert "response_time_seconds" in result


def test_answer_query_no_vector_store():
    with pytest.raises(ValueError):
        chat_service.answer_query("query", "history", None, None)
