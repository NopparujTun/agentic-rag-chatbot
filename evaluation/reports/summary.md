# Agentic RAG Evaluation Summary

This report contains the evaluation results of the Retrieval-Augmented Generation (RAG) system, generated dynamically against the CMU Registrar dataset.

## 1. Retrieval Accuracy Metrics
*Tested on 100 benchmark queries.*

| Strategy | Recall@1 | Recall@5 | Recall@10 | Precision@5 | MRR@10 |
|---|---|---|---|---|---|
| Dense Only | 0.8000 | 0.9400 | 0.9500 | 0.4200 | 0.8675 |
| BM25 Only | 0.4300 | 0.7400 | 0.9500 | 0.3200 | 0.5905 |
| Hybrid (RRF) | 0.6000 | 0.9300 | 0.9500 | 0.3940 | 0.7454 |
| Hybrid + Reranker | 0.9000 | 0.9500 | 0.9500 | 0.4300 | 0.9233 |

**Key Finding:** Cross-encoder reranking yields the highest accuracy, achieving an MRR@10 of 0.9233 (up from 0.8675 for dense-only).

## 2. Latency Metrics
*Averaged over 50 test iterations (run on local CPU environment).*

| Component | Avg Latency (ms) | P95 Latency (ms) | P99 Latency (ms) |
|---|---|---|---|
| Embedding Generation | 356.60 | 454.27 | 498.06 |
| BM25 Search | 0.19 | 0.27 | 0.34 |
| Vector Search (Pinecone) | 806.40 | 903.90 | 931.28 |
| Cross-Encoder Reranking | 4636.09 | 4837.22 | 4857.34 |
| E2E Hybrid (RRF) | 827.95 | 916.72 | 938.08 |
| E2E Hybrid (Reranker) | 4393.09 | 4601.54 | 4680.35 |

**Key Finding:** Standard Hybrid Retrieval (RRF) completes in ~828ms, making it suitable for real-time inference, while Cross-Encoder reranking significantly increases latency in a CPU environment (~4.39s) but maximizes accuracy.
