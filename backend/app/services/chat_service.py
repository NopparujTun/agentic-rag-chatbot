import time
import logging
from typing import Dict, Any

from app.rag.generator import generate_answer

logger = logging.getLogger(__name__)

def process_chat(
    query: str,
    chat_history: str,
    vector_store: Any,
    bm25_retriever: Any,
    reranker: Any
) -> Dict[str, Any]:
    """Encapsulates the business logic for the chat operation."""
    if vector_store is None:
        raise ValueError("Database not initialized. Please upload files first.")
         
    start_time = time.time()
    answer, retrieved_sources, steps_taken = generate_answer(
        query=query,
        vectorstore=vector_store,
        bm25_retriever=bm25_retriever,
        chat_history=chat_history,
        reranker=reranker
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
