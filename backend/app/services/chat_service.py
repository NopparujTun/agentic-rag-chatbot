import time
import logging
from typing import Any, Dict

from app.rag.generator import RAGAgent
from app.rag.retriever import PineconeRetriever

logger = logging.getLogger(__name__)

def answer_query(
    query: str,
    chat_history: str,
    vector_store: Any,
    reranker: Any,
) -> Dict[str, Any]:
    """Run the agentic RAG pipeline for one query and serialize the response."""
    if vector_store is None:
        raise ValueError("Database not initialized. Please upload files first.")

    retriever = PineconeRetriever(vector_store, reranker)
    agent = RAGAgent(retriever)

    start_time = time.time()
    answer, retrieved_sources, steps_taken = agent.generate(
        query=query,
        chat_history=chat_history,
    )
    response_time = time.time() - start_time

    serialized_sources = [
        {
            "content": doc.page_content,
            "metadata": doc.metadata
        }
        for doc in retrieved_sources
    ] if retrieved_sources else []

    serialized_steps = [
        {
            "tool": action.tool,
            "tool_input": action.tool_input,
            "observation": observation
        }
        for action, observation in steps_taken
    ] if steps_taken else []

    return {
        "answer": answer,
        "sources": serialized_sources,
        "steps": serialized_steps,
        "response_time_seconds": round(response_time, 2)
    }
