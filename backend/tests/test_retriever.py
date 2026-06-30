import pytest
from unittest.mock import MagicMock
from langchain_core.documents import Document

from app.rag import retriever

def test_pinecone_retriever_search_no_reranker():
    mock_vs = MagicMock()
    docs = [Document(page_content="doc1"), Document(page_content="doc2")]
    mock_vs.similarity_search.return_value = docs
    
    ret = retriever.PineconeRetriever(vectorstore=mock_vs, reranker=None)
    result = ret.search("query", k=1, fetch_k=2)
    
    assert len(result) == 1
    assert result[0] == docs[0]
    mock_vs.similarity_search.assert_called_once_with("query", k=2)

def test_pinecone_retriever_search_with_reranker():
    mock_vs = MagicMock()
    docs = [Document(page_content="doc1"), Document(page_content="doc2")]
    mock_vs.similarity_search.return_value = docs
    
    mock_reranker = MagicMock()
    # Reranker predicts higher score for doc2
    mock_reranker.predict.return_value = [0.1, 0.9]
    
    ret = retriever.PineconeRetriever(vectorstore=mock_vs, reranker=mock_reranker)
    result = ret.search("query", k=1, fetch_k=2)
    
    assert len(result) == 1
    assert result[0] == docs[1]
    mock_vs.similarity_search.assert_called_once_with("query", k=2)
    mock_reranker.predict.assert_called_once_with([["query", "doc1"], ["query", "doc2"]])
