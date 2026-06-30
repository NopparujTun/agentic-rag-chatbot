"""Pinecone retrieval with optional Cross-Encoder re-ranking."""

from typing import List, Optional

from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from sentence_transformers import CrossEncoder


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
