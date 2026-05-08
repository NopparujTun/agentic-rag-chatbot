"""Search tools for the LangGraph agent."""

import logging
import os
from typing import List, Set

from langchain_core.tools import tool
from langchain_core.documents import Document

from app.rag.retriever import HybridRetriever

logger = logging.getLogger(__name__)

def create_search_tool(retriever: HybridRetriever, retrieved_documents: List[Document], seen_document_contents: Set[str]):
    """Create a bounded search tool that updates the provided state collections."""
    
    @tool
    def search_knowledge_base(search_query: str) -> str:
        """Search the enterprise knowledge base for relevant documents.
        
        Use this to find context for the user's question. You can use it
        multiple times with different queries if needed. Provide specific,
        focused queries.
        """
        logger.info(f"Agent executing search_knowledge_base with query: '{search_query}'")
        found_documents = retriever.search(search_query, k=4, fetch_k=10)
        
        if not found_documents:
            return "No relevant documents found for this query. Try a different search strategy or broader keywords."
        
        new_documents = []
        for document in found_documents:
            if document.page_content not in seen_document_contents:
                seen_document_contents.add(document.page_content)
                new_documents.append(document)
        
        retrieved_documents.extend(new_documents)
        
        formatted_docs = []
        for index, document in enumerate(found_documents, 1):
            source_path = document.metadata.get('source', 'Unknown')
            file_name = os.path.basename(source_path)
            formatted_docs.append(f"--- Document {index} (Source: {file_name}) ---\n{document.page_content}")
        
        return "\n\n".join(formatted_docs)
        
    return search_knowledge_base
