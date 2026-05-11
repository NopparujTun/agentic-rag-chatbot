"""Pinecone retrieval with optional Cross-Encoder re-ranking."""

import logging
from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

def get_embedding_model(model_name: str, device: str) -> Embeddings:
    """Load and return a Pinecone embedding model."""
    logger.info("Loading Pinecone embedding model: %s", model_name)
    embeddings = PineconeEmbeddings(model=model_name)
    logger.info("Embedding model loaded successfully")
    return embeddings


def get_reranker(model_name: str = "BAAI/bge-reranker-v2-m3", device: str = "cpu") -> CrossEncoder:
    """Load a Cross-Encoder model for precision re-ranking."""
    logger.info("Loading Re-ranker model: %s (device=%s)", model_name, device)
    return CrossEncoder(model_name, max_length=512, device=device)


class PineconeRetriever:
    """A managed Pinecone retriever with optional precision re-ranking."""

    def __init__(
        self,
        vectorstore: PineconeVectorStore,
        reranker: Optional[CrossEncoder] = None,
    ):
        self.vectorstore = vectorstore
        self.reranker = reranker

    def search(
        self,
        query: str,
        k: int = 3,
        fetch_k: int = 8,
    ) -> List[Document]:
        documents = self.vectorstore.similarity_search(query, k=fetch_k)

        if self.reranker is not None and documents:
            documents = self._apply_reranking(query, documents)

        return documents[:k]

    def _apply_reranking(self, query: str, documents: List[Document]) -> List[Document]:
        query_document_pairs = [[query, document.page_content] for document in documents]
        rerank_scores = self.reranker.predict(query_document_pairs)
        
        scored_documents = sorted(zip(documents, rerank_scores), key=lambda item: item[1], reverse=True)
        return [doc for doc, score in scored_documents]
