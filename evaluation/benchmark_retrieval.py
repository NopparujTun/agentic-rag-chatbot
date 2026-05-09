import os
import sys
import json
import logging
from tqdm import tqdm
from dotenv import load_dotenv

# Add backend to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from app.core.config import load_config
from app.rag.retriever import get_embedding_model, get_reranker, HybridRetriever
from app.storage.vector_store import load_hybrid_store
from evaluation.utils.metrics import (
    is_relevant, calculate_mrr, calculate_recall_at_k,
    calculate_precision_at_k, calculate_ndcg_at_k
)

logging.basicConfig(level=logging.WARNING)

def run_retrieval_benchmark():
    print("Loading configuration...")
    config = load_config(os.path.join("backend", "config.yaml"))
    
    # Load dataset
    dataset_path = "cmu_registrar_eval_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print(f"Loaded dataset with {len(dataset)} queries.")

    # Initialize components
    print("Initializing retrieval components...")
    embedding_model = get_embedding_model(
        config["embedding"]["model_name"], 
        config["embedding"]["device"]
    )
    
    persist_dir = os.path.join("backend", config["vector_db"]["persist_directory"])
    vector_store, bm25_retriever = load_hybrid_store(
        embedding_model=embedding_model,
        persist_dir=persist_dir,
        index_name=config["vector_db"]["index_name"]
    )
    
    reranker = get_reranker()
    
    # Define retrievers to test
    strategies = {
        "Dense Only": HybridRetriever(vectorstore=vector_store, bm25_retriever=None, reranker=None),
        "BM25 Only": HybridRetriever(vectorstore=None, bm25_retriever=bm25_retriever, reranker=None), # This will fail if vectorstore is None, HybridRetriever doesn't support BM25 only cleanly. We will handle BM25 separately.
        "Hybrid (RRF)": HybridRetriever(vectorstore=vector_store, bm25_retriever=bm25_retriever, reranker=None),
        "Hybrid + Reranker": HybridRetriever(vectorstore=vector_store, bm25_retriever=bm25_retriever, reranker=reranker),
    }

    results = {strategy: {
        "Recall@1": [], "Recall@3": [], "Recall@5": [], "Recall@10": [],
        "Precision@5": [], "MRR@10": [], "nDCG@10": []
    } for strategy in strategies}
    
    per_query_results = []
    
    print("Running evaluation...")
    for item in tqdm(dataset, desc="Evaluating Queries"):
        query = item["query"]
        answer = item["answer"]
        keywords = item.get("keywords", [])
        
        query_res = {"id": item["id"], "query": query, "strategies": {}}
        
        for name, retriever in strategies.items():
            if name == "BM25 Only":
                if bm25_retriever:
                    # LangChain BM25Retriever doesn't take k natively in invoke, we set it
                    bm25_retriever.k = 10
                    docs = bm25_retriever.invoke(query)
                else:
                    docs = []
            else:
                docs = retriever.search(query, k=10, fetch_k=20)
                
            # Compute relevance for top 10
            rel_array = [is_relevant(doc.page_content, keywords, answer) for doc in docs]
            # Pad to 10 if less
            rel_array.extend([False] * (10 - len(rel_array)))
            
            # Compute metrics
            m_r1 = calculate_recall_at_k(rel_array, 1)
            m_r3 = calculate_recall_at_k(rel_array, 3)
            m_r5 = calculate_recall_at_k(rel_array, 5)
            m_r10 = calculate_recall_at_k(rel_array, 10)
            m_p5 = calculate_precision_at_k(rel_array, 5)
            m_mrr = calculate_mrr(rel_array[:10])
            m_ndcg = calculate_ndcg_at_k(rel_array, 10)
            
            results[name]["Recall@1"].append(m_r1)
            results[name]["Recall@3"].append(m_r3)
            results[name]["Recall@5"].append(m_r5)
            results[name]["Recall@10"].append(m_r10)
            results[name]["Precision@5"].append(m_p5)
            results[name]["MRR@10"].append(m_mrr)
            results[name]["nDCG@10"].append(m_ndcg)
            
            query_res["strategies"][name] = {
                "Recall@10": m_r10,
                "MRR@10": m_mrr
            }
            
        per_query_results.append(query_res)

    # Average results
    final_metrics = {}
    for strategy in strategies:
        final_metrics[strategy] = {
            metric: sum(values) / len(values) if values else 0.0
            for metric, values in results[strategy].items()
        }
        
    output_data = {
        "summary": final_metrics,
        "per_query": per_query_results
    }
    
    os.makedirs("evaluation/reports", exist_ok=True)
    with open("evaluation/reports/retrieval_metrics.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print("\n--- Retrieval Metrics Summary ---")
    for strategy, metrics in final_metrics.items():
        print(f"Strategy: {strategy}")
        for k, v in metrics.items():
            print(f"  {k}: {v:.4f}")
        print()

if __name__ == "__main__":
    run_retrieval_benchmark()
