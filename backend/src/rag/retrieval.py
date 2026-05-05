"""Hybrid vector + keyword store with Reciprocal Rank Fusion (RRF) and Re-ranking.

Provides functionalities to retrieve, save, load, and clear documents from
both Pinecone Vector Store and local BM25 indexes.
"""

import concurrent.futures
import logging
import os
import pickle
import shutil
from typing import Dict, List, Optional, Tuple

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)

# RRF smoothing constant (standard value from the original RRF paper).
DEFAULT_RRF_K = 60
BM25_FILENAME = "bm25_index.pkl"


def get_embedding_model(model_name: str, device: str) -> Embeddings:
    """Load and return a Pinecone embedding model.

    Args:
        model_name: The name of the Pinecone model to load.
        device: The computing device ('cpu', 'cuda'). Not strictly used by PineconeEmbeddings.

    Returns:
        The initialized embeddings model.
    """
    logger.info("Loading Pinecone embedding model: %s", model_name)
    embeddings = PineconeEmbeddings(model=model_name)
    logger.info("Embedding model loaded successfully")
    return embeddings


def get_reranker(model_name: str = "BAAI/bge-reranker-v2-m3", device: str = "cpu") -> CrossEncoder:
    """Load a Cross-Encoder model for precision re-ranking.

    Args:
        model_name: The HuggingFace model name for the reranker.
        device: The computing device ('cpu', 'cuda').

    Returns:
        The initialized CrossEncoder model.
    """
    logger.info("Loading Re-ranker model: %s (device=%s)", model_name, device)
    return CrossEncoder(model_name, max_length=512, device=device)


class HybridRetriever:
    """A managed hybrid retriever combining dense and sparse search."""

    def __init__(
        self,
        vectorstore: PineconeVectorStore,
        bm25_retriever: Optional[BM25Retriever] = None,
        reranker: Optional[CrossEncoder] = None,
        rrf_k: int = DEFAULT_RRF_K,
    ):
        """Initialize the hybrid retriever.

        Args:
            vectorstore: The Pinecone vector store for dense retrieval.
            bm25_retriever: The optional BM25 retriever for sparse retrieval.
            reranker: The optional CrossEncoder for reranking results.
            rrf_k: The smoothing constant for Reciprocal Rank Fusion.
        """
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
        """Perform a hybrid search with optional re-ranking.

        Args:
            query: The search string.
            k: The final number of documents to return.
            fetch_k: The number of documents to fetch from each retriever initially.

        Returns:
            A list of retrieved and optionally reranked LangChain Documents.
        """
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_vector = executor.submit(self.vectorstore.similarity_search, query, k=fetch_k)
            
            if self.bm25_retriever is not None:
                self.bm25_retriever.k = fetch_k
                future_bm25 = executor.submit(self.bm25_retriever.invoke, query)
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
        """Combine results using Reciprocal Rank Fusion.

        Args:
            vector_docs: Documents retrieved from the vector store.
            bm25_docs: Documents retrieved from the BM25 store.
            fetch_k: Total number of documents to return after fusion.

        Returns:
            A fused list of Documents ordered by their RRF score.
        """
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
        """Re-rank documents using the Cross-Encoder model.

        Args:
            query: The original search query.
            documents: The initial list of retrieved documents.

        Returns:
            The list of documents ordered by their reranker score.
        """
        query_document_pairs = [[query, document.page_content] for document in documents]
        rerank_scores = self.reranker.predict(query_document_pairs)
        
        scored_documents = sorted(zip(documents, rerank_scores), key=lambda item: item[1], reverse=True)
        return [doc for doc, score in scored_documents]


def save_hybrid_store(
    chunks: List[Document],
    embedding_model: Embeddings,
    persist_dir: str,
    index_name: str,
) -> Tuple[PineconeVectorStore, BM25Retriever]:
    """Index document chunks into Pinecone and save a local BM25 index.

    Args:
        chunks: The list of chunked documents to ingest.
        embedding_model: The embedding model for vector generation.
        persist_dir: The local directory to save the BM25 index.
        index_name: The name of the Pinecone index.

    Returns:
        A tuple containing the PineconeVectorStore and BM25Retriever.
    """
    os.makedirs(persist_dir, exist_ok=True)

    logger.info("Uploading %d chunks to Pinecone index '%s'", len(chunks), index_name)
    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        index_name=index_name,
    )

    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_file_path = os.path.join(persist_dir, BM25_FILENAME)
    
    with open(bm25_file_path, "wb") as file_handle:
        pickle.dump(bm25_retriever, file_handle)

    logger.info("Saved BM25 index to %s", bm25_file_path)
    return vector_store, bm25_retriever


def load_hybrid_store(
    embedding_model: Embeddings,
    persist_dir: str,
    index_name: str,
) -> Tuple[PineconeVectorStore, Optional[BM25Retriever]]:
    """Connect to an existing Pinecone index and load the local BM25 index.

    Args:
        embedding_model: The embedding model to connect with Pinecone.
        persist_dir: The local directory storing the BM25 index.
        index_name: The name of the Pinecone index.

    Returns:
        A tuple containing the PineconeVectorStore and an optional BM25Retriever.
    """
    logger.info("Connecting to Pinecone index '%s'", index_name)
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_model,
    )

    bm25_file_path = os.path.join(persist_dir, BM25_FILENAME)
    bm25_retriever = None
    
    if os.path.exists(bm25_file_path):
        with open(bm25_file_path, "rb") as file_handle:
            bm25_retriever = pickle.load(file_handle)
        logger.info("Loaded BM25 index from %s", bm25_file_path)
    else:
        logger.warning("BM25 index not found at %s — keyword search disabled", bm25_file_path)

    return vector_store, bm25_retriever


def clear_hybrid_store(vectorstore: PineconeVectorStore, persist_dir: str) -> None:
    """Clear all vectors from Pinecone and delete local BM25 directory.

    Args:
        vectorstore: The PineconeVectorStore instance.
        persist_dir: The local directory containing the BM25 index.
    """
    logger.info("Clearing Knowledge Base: Vector database and BM25.")
    
    try:
        vectorstore.delete(delete_all=True)
        logger.info("Deleted all vectors from Pinecone.")
    except Exception as exception:
        logger.error("Failed to delete from Pinecone: %s", exception)

    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        os.makedirs(persist_dir, exist_ok=True)
        logger.info("Cleared BM25 index directory: %s", persist_dir)
