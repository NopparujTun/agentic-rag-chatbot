"""Storage operations for vector and keyword databases."""

import logging
import os
import shutil
from typing import List, Tuple, Optional, Any

from elasticsearch import Elasticsearch, helpers
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore

logger = logging.getLogger(__name__)

def get_es_client() -> Elasticsearch:
    es_url = os.environ.get("ELASTICSEARCH_URL", "http://elasticsearch:9200")
    return Elasticsearch(es_url)

class ElasticsearchBM25Retriever:
    """Custom Elasticsearch BM25 Retriever."""
    def __init__(self, index_name: str):
        self.index_name = index_name + "_bm25"
        self.client = get_es_client()
        
    def _create_index_if_not_exists(self):
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(
                index=self.index_name,
                body={
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "default": {
                                    "type": "standard"
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "page_content": {"type": "text", "analyzer": "standard"},
                            "metadata": {"type": "object", "enabled": True}
                        }
                    }
                }
            )
            
    def add_documents(self, documents: List[Document]):
        self._create_index_if_not_exists()
        actions = [
            {
                "_index": self.index_name,
                "_source": {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata
                }
            }
            for doc in documents
        ]
        helpers.bulk(self.client, actions)
        self.client.indices.refresh(index=self.index_name)
        
    def invoke(self, query: str, top_k: int = 5) -> List[Document]:
        if not self.client.indices.exists(index=self.index_name):
            return []
            
        body = {
            "query": {
                "match": {
                    "page_content": query
                }
            },
            "size": top_k
        }
        response = self.client.search(index=self.index_name, body=body)
        hits = response["hits"]["hits"]
        return [
            Document(
                page_content=hit["_source"]["page_content"],
                metadata=hit["_source"].get("metadata", {})
            )
            for hit in hits
        ]

def save_hybrid_store(
    chunks: List[Document],
    embedding_model: Embeddings,
    persist_dir: str,
    index_name: str,
) -> Tuple[PineconeVectorStore, Any]:
    """Index document chunks into Pinecone and Elasticsearch."""
    logger.info("Uploading %d chunks to Pinecone index '%s'", len(chunks), index_name)
    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        index_name=index_name,
    )

    bm25_retriever = ElasticsearchBM25Retriever(index_name=index_name)
    bm25_retriever.add_documents(chunks)
    
    logger.info("Saved chunks to Elasticsearch BM25 index.")
    return vector_store, bm25_retriever


def load_hybrid_store(
    embedding_model: Embeddings,
    persist_dir: str,
    index_name: str,
) -> Tuple[PineconeVectorStore, Any]:
    """Connect to an existing Pinecone index and Elasticsearch BM25 index."""
    logger.info("Connecting to Pinecone index '%s'", index_name)
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_model,
    )

    bm25_retriever = ElasticsearchBM25Retriever(index_name=index_name)
    logger.info("Connected to Elasticsearch BM25 index")

    return vector_store, bm25_retriever


def clear_hybrid_store(vectorstore: PineconeVectorStore, persist_dir: str) -> None:
    """Clear all vectors from Pinecone and Elasticsearch."""
    logger.info("Clearing Knowledge Base: Vector database and BM25.")
    
    try:
        vectorstore.delete(delete_all=True)
        logger.info("Deleted all vectors from Pinecone.")
    except Exception as exception:
        logger.error("Failed to delete from Pinecone: %s", exception)

    try:
        es = get_es_client()
        # Delete all indices that look like bm25 indices
        es.indices.delete(index="*_bm25", ignore_unavailable=True)
        logger.info("Cleared Elasticsearch BM25 index.")
    except Exception as exception:
        logger.error("Failed to clear Elasticsearch: %s", exception)
