import math
from typing import List

def is_relevant(chunk_text: str, expected_keywords: List[str], answer: str) -> bool:
    """
    Determine if a retrieved chunk is relevant to the ground truth.
    We check if the chunk contains at least 50% of the expected keywords, 
    or if the chunk contains the exact answer text.
    """
    if not expected_keywords:
        # If no keywords, check if answer is in chunk
        return answer.lower() in chunk_text.lower()
        
    chunk_lower = chunk_text.lower()
    
    # Check for answer inclusion (direct match)
    if answer and len(answer) > 5 and answer.lower() in chunk_lower:
        return True
        
    hits = sum(1 for kw in expected_keywords if kw.lower() in chunk_lower)
    hit_ratio = hits / len(expected_keywords)
    
    return hit_ratio >= 0.5

def calculate_mrr(retrieved_relevance: List[bool]) -> float:
    """Calculate Mean Reciprocal Rank for a single query."""
    for i, rel in enumerate(retrieved_relevance):
        if rel:
            return 1.0 / (i + 1)
    return 0.0

def calculate_recall_at_k(retrieved_relevance: List[bool], k: int) -> float:
    """Calculate Recall@K. (1.0 if relevant chunk is in top K, else 0.0)"""
    return 1.0 if any(retrieved_relevance[:k]) else 0.0

def calculate_precision_at_k(retrieved_relevance: List[bool], k: int) -> float:
    """Calculate Precision@K."""
    top_k = retrieved_relevance[:k]
    if not top_k:
        return 0.0
    return sum(top_k) / k

def calculate_ndcg_at_k(retrieved_relevance: List[bool], k: int) -> float:
    """Calculate nDCG@K for binary relevance."""
    dcg = 0.0
    for i, rel in enumerate(retrieved_relevance[:k]):
        if rel:
            dcg += 1.0 / math.log2(i + 2) # i+2 because rank starts at 1 (index 0 -> log2(2)=1)
            
    # Ideal DCG for binary relevance: assume 1 relevant doc
    idcg = 1.0 / math.log2(2)
    return dcg / idcg if idcg > 0 else 0.0
