import pytest
from unittest.mock import patch, MagicMock
from app.tools import search
from langchain_core.documents import Document

def test_create_search_tool():
    mock_retriever = MagicMock()
    docs = [
        Document(page_content="doc1 content", metadata={"source": "/path/to/test.pdf"}),
        Document(page_content="doc2 content", metadata={"source": "test2.pdf"})
    ]
    mock_retriever.search.return_value = docs
    
    retrieved_docs = []
    seen = set()
    
    search_tool = search.create_search_tool(mock_retriever, retrieved_docs, seen)
    assert search_tool.name == "search_knowledge_base"
    
    result = search_tool.invoke({"search_query": "test query"})
    
    assert "Document 1" in result
    assert "test.pdf" in result
    assert "doc1 content" in result
    assert "Document 2" in result
    
    assert len(retrieved_docs) == 2
    assert "doc1 content" in seen
    
    # Run again with same docs to test seen logic
    result2 = search_tool.invoke({"search_query": "test query 2"})
    assert len(retrieved_docs) == 2 # Should not add duplicates

def test_create_search_tool_no_results():
    mock_retriever = MagicMock()
    mock_retriever.search.return_value = []
    
    retrieved_docs = []
    seen = set()
    
    search_tool = search.create_search_tool(mock_retriever, retrieved_docs, seen)
    result = search_tool.invoke({"search_query": "test query"})
    
    assert "No relevant documents found" in result
    assert len(retrieved_docs) == 0
