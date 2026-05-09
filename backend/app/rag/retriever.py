"""Hybrid vector + keyword store with Reciprocal Rank Fusion (RRF) and Re-ranking."""

import concurrent.futures
import logging
from typing import Dict, List, Optional, Any

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

# RRF smoothing constant (standard value from the original RRF paper).
DEFAULT_RRF_K = 60


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


class HybridRetriever:
    """A managed hybrid retriever combining dense and sparse search."""

    def __init__(
        self,
        vectorstore: PineconeVectorStore,
        bm25_retriever: Optional[Any] = None,
        reranker: Optional[CrossEncoder] = None,
        rrf_k: int = DEFAULT_RRF_K,
    ):
        self.vectorstore = vectorstore
        self.bm25_retriever = bm25_retriever
        self.reranker = reranker
        self.rrf_k = rrf_k

    def search(
        self,
        query: str,
        k: int = 3,
        fetch_k: int = 8,
    ) -> List[Document]:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_vector = executor.submit(self.vectorstore.similarity_search, query, k=fetch_k)
            
            if self.bm25_retriever is not None:
                # Custom Elasticsearch BM25 Retriever
                future_bm25 = executor.submit(self.bm25_retriever.invoke, query, top_k=fetch_k)
            else:
                future_bm25 = None
            
            vector_documents = future_vector.result()
            bm25_documents = future_bm25.result() if future_bm25 else []

        if not bm25_documents:
            fused_documents = vector_documents
        else:
            fused_documents = self._apply_rrf(vector_documents, bm25_documents, fetch_k)

        if self.reranker is not None and fused_documents:
            fused_documents = self._apply_reranking(query, fused_documents)

        return fused_documents[:k]

    def _apply_rrf(
        self, 
        vector_docs: List[Document], 
        bm25_docs: List[Document], 
        fetch_k: int
    ) -> List[Document]:
        document_scores: Dict[str, float] = {}
        document_mapping: Dict[str, Document] = {}

        def _compute_rrf(retrieved_docs: List[Document]) -> None:
            for rank_index, document in enumerate(retrieved_docs):
                content = document.page_content
                document_mapping[content] = document
                document_scores[content] = document_scores.get(content, 0.0) + (1.0 / (rank_index + 1 + self.rrf_k))

        _compute_rrf(vector_docs)
        _compute_rrf(bm25_docs)

        sorted_results = sorted(document_scores.items(), key=lambda item: item[1], reverse=True)
        return [document_mapping[content] for content, _ in sorted_results[:fetch_k]]

    def _apply_reranking(self, query: str, documents: List[Document]) -> List[Document]:
        query_document_pairs = [[query, document.page_content] for document in documents]
        rerank_scores = self.reranker.predict(query_document_pairs)
        
        scored_documents = sorted(zip(documents, rerank_scores), key=lambda item: item[1], reverse=True)
        return [doc for doc, score in scored_documents]
