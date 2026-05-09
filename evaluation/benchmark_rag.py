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
from app.rag.generator import RAGGenerator
from app.rag.retriever import get_embedding_model, get_reranker, HybridRetriever
from app.storage.vector_store import load_hybrid_store
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.WARNING)

def calculate_token_overlap(gen_text: str, ref_text: str) -> float:
    """Lightweight text similarity (Jaccard index of words)"""
    gen_tokens = set(gen_text.lower().split())
    ref_tokens = set(ref_text.lower().split())
    if not gen_tokens or not ref_tokens:
        return 0.0
    intersection = gen_tokens.intersection(ref_tokens)
    union = gen_tokens.union(ref_tokens)
    return len(intersection) / len(union)

def calculate_keyword_recall(gen_text: str, keywords: list) -> float:
    """Measure how many expected keywords appeared in the generation"""
    if not keywords:
        return 0.0
    gen_lower = gen_text.lower()
    hits = sum(1 for kw in keywords if kw.lower() in gen_lower)
    return hits / len(keywords)

def benchmark_rag():
    print("Loading configuration...")
    config = load_config(os.path.join("backend", "config.yaml"))
    
    # Load dataset
    dataset_path = "cmu_registrar_eval_dataset.json"
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    # Take a smaller subset for RAG eval to save API costs
    queries = dataset[:15]
    print(f"Running E2E RAG evaluation on {len(queries)} queries.")

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
    retriever = HybridRetriever(vectorstore=vector_store, bm25_retriever=bm25_retriever, reranker=reranker)
    generator = RAGGenerator()
    
    results = {
        "Answer_Correctness_Proxy": [],
        "Faithfulness_Keyword_Recall": [],
        "Hallucination_Proxy": []
    }
    
    for item in tqdm(queries, desc="Evaluating RAG"):
        q = item["query"]
        ref_answer = item["answer"]
        keywords = item.get("keywords", [])
        
        docs = retriever.search(q, k=3, fetch_k=10)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # We invoke the generator chain directly
        try:
            # We mock the state dict expected by the generator
            state = {
                "messages": [HumanMessage(content=q)],
                "context": context,
                "current_query": q,
                "language": "th"
            }
            res_state = generator.generate(state)
            generated_answer = res_state["messages"][-1].content
            
            # Metrics
            overlap = calculate_token_overlap(generated_answer, ref_answer)
            results["Answer_Correctness_Proxy"].append(overlap)
            
            kw_recall = calculate_keyword_recall(generated_answer, keywords)
            results["Faithfulness_Keyword_Recall"].append(kw_recall)
            
            # A simple proxy for hallucination: if it generates a lot of text but captures no keywords or overlap
            if kw_recall == 0 and len(generated_answer.split()) > 20:
                results["Hallucination_Proxy"].append(1.0) # likely hallucinated
            else:
                results["Hallucination_Proxy"].append(0.0)
                
        except Exception as e:
            logging.error(f"Failed to generate for query '{q}': {e}")
            continue

    summary = {
        "Answer_Correctness_Proxy": sum(results["Answer_Correctness_Proxy"]) / len(results["Answer_Correctness_Proxy"]) if results["Answer_Correctness_Proxy"] else 0,
        "Faithfulness_Keyword_Recall": sum(results["Faithfulness_Keyword_Recall"]) / len(results["Faithfulness_Keyword_Recall"]) if results["Faithfulness_Keyword_Recall"] else 0,
        "Hallucination_Rate_Proxy": sum(results["Hallucination_Proxy"]) / len(results["Hallucination_Proxy"]) if results["Hallucination_Proxy"] else 0,
    }
    
    os.makedirs("evaluation/reports", exist_ok=True)
    with open("evaluation/reports/rag_eval.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    print("\n--- RAG Quality Benchmark Summary ---")
    for k, v in summary.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    benchmark_rag()
