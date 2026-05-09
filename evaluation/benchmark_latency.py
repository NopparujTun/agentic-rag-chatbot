import os
import sys
import json
import time
import numpy as np
import logging
from tqdm import tqdm
from dotenv import load_dotenv

# Add backend to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from app.core.config import load_config
from app.rag.retriever import get_embedding_model, get_reranker, HybridRetriever
from app.storage.vector_store import load_hybrid_store

logging.basicConfig(level=logging.WARNING)

def benchmark_latency():
    print("Loading configuration...")
    config = load_config(os.path.join("backend", "config.yaml"))
    
    # Load dataset
    dataset_path = "cmu_registrar_eval_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    queries = [item["query"] for item in dataset]
    # Use subset for faster latency testing or all if small
    if len(queries) > 50:
        queries = queries[:50]
        
    print(f"Benchmarking with {len(queries)} queries.")

    # Initialize components
    print("Initializing components...")
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
    
    retriever_hybrid_rrf = HybridRetriever(vectorstore=vector_store, bm25_retriever=bm25_retriever, reranker=None)
    retriever_hybrid_rerank = HybridRetriever(vectorstore=vector_store, bm25_retriever=bm25_retriever, reranker=reranker)
    
    metrics = {
        "Embedding Generation": [],
        "BM25 Search": [],
        "Vector Search": [],
        "Reranking": [],
        "E2E Hybrid + RRF": [],
        "E2E Hybrid + Reranker": []
    }

    # Warmup
    print("Running warmup...")
    for q in queries[:2]:
        embedding_model.embed_query(q)
        if bm25_retriever:
            bm25_retriever.invoke(q)
        vector_store.similarity_search(q, k=10)
        retriever_hybrid_rrf.search(q)
        retriever_hybrid_rerank.search(q)
        
    print("Running latency benchmark...")
    for q in tqdm(queries, desc="Latency Runs"):
        # 1. Embedding
        t0 = time.perf_counter()
        embedding_model.embed_query(q)
        t1 = time.perf_counter()
        metrics["Embedding Generation"].append((t1 - t0) * 1000)
        
        # 2. BM25
        t0 = time.perf_counter()
        if bm25_retriever:
            bm25_retriever.invoke(q)
        t1 = time.perf_counter()
        metrics["BM25 Search"].append((t1 - t0) * 1000)
        
        # 3. Vector Search
        t0 = time.perf_counter()
        docs = vector_store.similarity_search(q, k=10)
        t1 = time.perf_counter()
        metrics["Vector Search"].append((t1 - t0) * 1000)
        
        # 4. Reranking (mock a pair based on retrieved docs)
        pairs = [[q, doc.page_content] for doc in docs[:10]]
        t0 = time.perf_counter()
        if reranker and pairs:
            reranker.predict(pairs)
        t1 = time.perf_counter()
        metrics["Reranking"].append((t1 - t0) * 1000)
        
        # 5. E2E Hybrid (RRF)
        t0 = time.perf_counter()
        retriever_hybrid_rrf.search(q)
        t1 = time.perf_counter()
        metrics["E2E Hybrid + RRF"].append((t1 - t0) * 1000)
        
        # 6. E2E Hybrid (Reranker)
        t0 = time.perf_counter()
        retriever_hybrid_rerank.search(q)
        t1 = time.perf_counter()
        metrics["E2E Hybrid + Reranker"].append((t1 - t0) * 1000)

    # Process metrics
    summary = {}
    for k, v in metrics.items():
        if not v:
            continue
        v_np = np.array(v)
        summary[k] = {
            "avg_ms": float(np.mean(v_np)),
            "p95_ms": float(np.percentile(v_np, 95)),
            "p99_ms": float(np.percentile(v_np, 99))
        }
        
    os.makedirs("evaluation/reports", exist_ok=True)
    with open("evaluation/reports/latency_metrics.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print("\n--- Latency Benchmark Summary ---")
    for k, v in summary.items():
        print(f"{k}: Avg={v['avg_ms']:.2f}ms | P95={v['p95_ms']:.2f}ms | P99={v['p99_ms']:.2f}ms")

if __name__ == "__main__":
    benchmark_latency()
