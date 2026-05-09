# Enterprise Smart Knowledge-Base: Production Evolution Roadmap

This document outlines the comprehensive, deep-technical roadmap required to transform the current Agentic RAG prototype into a production-grade, highly available, secure, and observable Enterprise LLMOps Platform.

---

## 1. Executive Summary

### Current State Assessment
The existing system is a sophisticated **Agentic MVP (Minimum Viable Product)**. It excels in AI capability (LangGraph orchestration, Hybrid RRF retrieval, VLM ingestion, Thai NLP integration) but currently operates as a stateful, monolithic local server. 

**Maturity Categorization:** High AI Complexity / Low Infrastructure Maturity.

### Target State Vision
A cloud-native, stateless, distributed microservices architecture designed for B2B SaaS or internal enterprise deployment. The platform must support horizontal scaling, robust tenant isolation, asynchronous background processing, and comprehensive observability for both traditional infrastructure and LLMOps.

---

## 2. Current Architecture Review & Technical Debt

### Core Strengths to Preserve
1.  **Agentic ReAct Loop:** The LangGraph implementation effectively mitigates hallucinations by enforcing source grounding and iterative retrieval.
2.  **Retrieval Pipeline:** The combination of Dense Vectors (Pinecone) + Sparse Vectors (BM25) + Cross-Encoder reranking provides exceptional MRR@10.
3.  **VLM Ingestion:** The use of Gemini for complex PDF extraction ensures high-fidelity data capture.

### Architectural Weaknesses (Blockers for Production)
1.  **Stateful API Layer:**
    *   **Issue:** `main.py` loads the embedding model and reranker into the FastAPI `app.state` during lifespan initialization. This locks heavy ML models into the synchronous web server process, preventing independent scaling of the API and Inference layers.
    *   **Issue:** Documents are saved directly to a local file system (`uploaded_docs`).
    *   **Issue:** BM25 data is serialized to a local disk (`./local_bm25_data`).
    *   **Result:** The application cannot be replicated across multiple pods/servers. It is horizontally unscalable.
2.  **Synchronous Ingestion:**
    *   **Issue:** The `/api/upload` endpoint executes the heavy `run_ingestion_pipeline` synchronously. Uploading a 50-page PDF will trigger HTTP timeouts (typically >30s) and block ASGI worker threads.
3.  **Security & Isolation:**
    *   **Issue:** No authentication mechanism.
    *   **Issue:** All documents exist in a single global Pinecone index (`"main"`). There is zero logical isolation preventing Cross-Tenant Data Leakage.

---

## 3. Production Readiness Gap Analysis

| Category | Specific Gap | Risk Level | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Scalability** | Stateful local disk usage (BM25, Uploads). | **Critical** | Migrate to S3 (uploads) and Elasticsearch (BM25). |
| **Compute** | Heavy models loaded in API process. | **Critical** | Decouple inference into dedicated gRPC/HTTP microservices or utilize managed serverless GPU endpoints. |
| **Async Tasks** | Synchronous file processing via HTTP. | **Critical** | Implement Celery + Redis/RabbitMQ for background job processing. |
| **Security** | No AuthN/AuthZ. Open CORS. | **Critical** | Implement OAuth2/JWT. Enforce tenant ID routing. |
| **Reliability** | No retry logic for external API calls. | **High** | Implement `Tenacity` (exponential backoff) and Circuit Breakers. |
| **Observability** | Standard `print`/`logger` only. | **High** | Implement OpenTelemetry (OTel) for distributed tracing. Structured JSON logging. |
| **Deployment** | Run manually via `uvicorn`. | **High** | Dockerize. Create Kubernetes Helm Charts. Implement CI/CD. |
| **Cost Control** | Redundant LLM calls for repeated queries. | **Medium** | Implement Semantic Caching via Redis. |

---

## 4. Proposed Target Architecture

The architecture will transition to an event-driven, distributed model.

### Component Breakdown

#### 1. API & Edge Layer
*   **API Gateway (e.g., Kong / AWS API Gateway):** Handles TLS termination, rate limiting (Redis-backed), and JWT validation.
*   **Core API Service (FastAPI):** Stateless web server. Validates requests, interacts with the DB, triggers Celery tasks, and orchestrates LangGraph execution.

#### 2. Asynchronous Worker Layer
*   **Message Broker (Redis / RabbitMQ):** Manages task queues (`ingestion_queue`, `batch_eval_queue`).
*   **Worker Nodes (Celery):** Dedicated processes (potentially GPU-enabled) that pull files from S3, run Docling/Gemini VLM, compute embeddings, and push to Pinecone/Elasticsearch.

#### 3. Storage & State Layer
*   **Relational DB (PostgreSQL):** Stores Users, Organizations, RBAC roles, Chat Sessions, Message History, and Document Metadata.
*   **Object Store (AWS S3 / MinIO):** Stores raw uploaded files and extracted images.
*   **Vector DB (Pinecone):** Stores dense embeddings. *Crucially, every vector must have a `tenant_id` metadata tag.*
*   **Sparse DB (Elasticsearch / OpenSearch):** Replaces local BM25. Handles scalable keyword indexing.

#### 4. Model & Inference Layer
*   **LLM Gateway (LiteLLM):** A centralized proxy for all LLM calls (Typhoon, Gemini, OpenAI) providing:
    *   Failover routing (e.g., if Typhoon is down, fallback to GPT-4o).
    *   Semantic Caching.
    *   Token usage tracking and cost attribution per tenant.

---

## 5. Infrastructure & DevOps Roadmap

### 5.1 Containerization Strategy
*   **Frontend:** Multi-stage build. `npm run build` -> Nginx Alpine serving static assets.
*   **Backend API:** Distroless Python image. Gunicorn with Uvicorn workers (`gunicorn -k uvicorn.workers.UvicornWorker`).
*   **Backend Worker:** Separate container image running `celery -A app.worker worker --loglevel=info`.

### 5.2 Kubernetes (K8s) Orchestration
*   **Helm Charts:** Create modular charts for the platform.
*   **Autoscaling:**
    *   API Pods: HPA based on CPU/Memory utilization.
    *   Worker Pods: KEDA (Kubernetes Event-driven Autoscaling) based on the Redis/RabbitMQ queue length.
*   **Probes:** Implement rigorous `/health/live` and `/health/ready` endpoints that verify DB, Redis, and Pinecone connectivity.

### 5.3 CI/CD Pipeline (GitHub Actions)
*   **PR Checks:** `ruff check`, `mypy`, `pytest` (unit tests), frontend `tsc`.
*   **Build:** Build and push Docker images to a registry (GHCR/ECR).
*   **Deployment:** GitOps driven via ArgoCD to distinct environments (Staging -> Prod).

---

## 6. Observability & Reliability Plan

### 6.1 Monitoring Stack
*   **Logs:** Migrate `logging` to structured JSON using `structlog`. Aggregate via Promtail/Loki or FluentBit/Elasticsearch.
*   **Metrics:** Expose `/metrics` endpoint via `prometheus_client`. Track:
    *   `http_request_duration_seconds`
    *   `llm_token_usage_total`
    *   `celery_tasks_pending`
*   **Tracing:** Integrate `opentelemetry-instrumentation-fastapi`. Inject trace IDs into headers and logs to track a request from UI -> API -> LLM -> DB.

### 6.2 Resiliency Mechanisms
*   **Retries:** Wrap Pinecone and LLM calls in `@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(5))` using the `tenacity` library.
*   **Timeouts:** Enforce strict timeouts on all external network requests to prevent hanging threads.
*   **Dead Letter Queues (DLQ):** Failed celery ingestion tasks must be routed to a DLQ for manual inspection and replay.

---

## 7. Retrieval & NLP Enhancement Roadmap

### 7.1 Elasticsearch Migration (Replacing BM25)
*   **Action:** Deprecate the `Rank BM25` python library.
*   **Implementation:** Deploy OpenSearch. When a chunk is embedded, index it simultaneously in Pinecone and OpenSearch using the same unique Chunk ID and `tenant_id`.
*   **Retrieval:** The `HybridRetriever` will issue parallel async requests to Pinecone and OpenSearch, merging the results before RRF.

### 7.2 Semantic Caching
*   **Architecture:** Implement `GPTCache` or LangChain's Redis Cache.
*   **Flow:** Before invoking the Agent, hash the query and search Redis for a semantically similar previous query (threshold > 0.95 cosine similarity). If found, return the cached answer instantly.

### 7.3 Advanced RAG Techniques
*   **Self-Querying:** Train the agent to translate natural language into Pinecone metadata filters (e.g., "Summarize the Q3 report" -> `{"document_type": "report", "quarter": "Q3"}`).
*   **Contextual Compression:** Use an LLM to prune irrelevant sentences from retrieved chunks before sending them to the final reasoning prompt, drastically reducing token costs.

---

## 8. LLMOps & Evaluation Roadmap

### 8.1 LLM Observability
*   **Tooling:** Integrate **LangSmith** or **Phoenix**.
*   **Goal:** Capture the exact input/output of every node in the LangGraph, the exact context chunks retrieved, and the generation latency.

### 8.2 Continuous Evaluation
*   **Tooling:** **Ragas** or **DeepEval**.
*   **Pipeline:** Create a golden dataset of 100 benchmark queries. Run a nightly CI job that evaluates the pipeline against:
    *   *Faithfulness:* Does the answer hallucinate beyond the retrieved context?
    *   *Answer Relevance:* Does the answer address the actual user query?
    *   *Context Precision:* Were the relevant chunks ranked at the top?

### 8.3 Prompt Management
*   Move prompts from hardcoded strings in `generator.py` to a managed Prompt Registry (e.g., Langfuse). This allows non-engineers to iterate on system prompts without requiring a code deployment.

---

## 9. Security & Enterprise Features

### 9.1 Multi-Tenancy (Logical Isolation)
*   **Auth:** Implement Auth0/OIDC. Every request must carry a Bearer JWT.
*   **Middleware:** Extract `tenant_id` from the JWT and inject it into the `request.state`.
*   **Enforcement:** 
    *   PostgreSQL: Use Row-Level Security (RLS) based on `tenant_id`.
    *   Pinecone: Pass `filter={"tenant_id": {"$eq": current_tenant}}` on every query.

### 9.2 API Security
*   **Rate Limiting:** Implement `slowapi` (Redis backed) to throttle requests per tenant (e.g., 50 chat messages per minute).
*   **File Sanitization:** Validate magic bytes of uploaded files, enforce strict size limits (e.g., max 20MB), and scan for malicious payloads before uploading to S3.

---

## 10. Prioritized Multi-Phase Implementation Plan

### Phase 1: Containerization & State Decoupling (Weeks 1-3)
**Goal:** Achieve a stateless, runnable Docker environment.
1.  **Task 1.1:** Write `Dockerfile` for Backend (FastAPI).
2.  **Task 1.2:** Write `Dockerfile` for Frontend (Vite/Nginx).
3.  **Task 1.3:** Setup local `docker-compose.yml` including Postgres and MinIO (local S3).
4.  **Task 1.4:** Refactor `main.py` lifespan. Move heavy model loading to lazy-loading or separate processes.
5.  **Task 1.5:** Refactor `/api/upload` to write files to MinIO/S3 instead of local `uploaded_docs`.

### Phase 2: Asynchronous Architecture (Weeks 4-6)
**Goal:** Fix the ingestion bottleneck and prepare for scaling.
1.  **Task 2.1:** Add Redis to `docker-compose.yml`. Setup Celery in the backend.
2.  **Task 2.2:** Refactor `ingestion_service.py` into Celery tasks. `/api/upload` now returns a `task_id` immediately.
3.  **Task 2.3:** Implement a GET `/api/tasks/{task_id}` endpoint for the frontend to poll upload status.
4.  **Task 2.4:** Replace local BM25 with Elasticsearch (add to compose, rewrite `retriever.py` sparse search logic).

### Phase 3: Security & Multi-Tenancy (Weeks 7-9)
**Goal:** Secure the platform for multi-user operation.
1.  **Task 3.1:** Integrate SQLAlchemy/Postgres for User and Organization models.
2.  **Task 3.2:** Implement JWT Authentication middleware.
3.  **Task 3.3:** Refactor Pinecone operations in `vector_store.py` to strictly enforce `tenant_id` metadata filtering.
4.  **Task 3.4:** Refactor Elasticsearch operations to enforce `tenant_id` routing.
5.  **Task 3.5:** Update Frontend context to manage Auth state and pass Bearer tokens.

### Phase 4: Observability, LLMOps, and CI/CD (Weeks 10-12)
**Goal:** Production readiness and day-2 operations capability.
1.  **Task 4.1:** Integrate LangSmith SDK into LangGraph nodes in `generator.py`.
2.  **Task 4.2:** Implement structured JSON logging (`structlog`).
3.  **Task 4.3:** Add `prometheus_fastapi_instrumentator` for metrics.
4.  **Task 4.4:** Create GitHub Actions workflows for CI (lint, test, build).
5.  **Task 4.5:** Implement Semantic Caching via `LiteLLM` or Redis directly.