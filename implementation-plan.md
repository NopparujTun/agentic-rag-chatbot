# Simplified Production Refactor Plan

## Overview

The previous architecture became overly complex for the current scale of the application.

Although the system gained enterprise-level infrastructure features, it resulted in:

- Worse performance
- Higher RAM usage
- Slower local development
- Increased Docker complexity
- Harder debugging
- More operational overhead

The platform will now transition back to a lean, high-performance architecture focused on simplicity and maintainability.

---

# Core Architecture Direction

## Keep

- FastAPI
- Vue + Vite
- LangGraph
- Pinecone
- Gemini VLM ingestion
- Cross-Encoder reranking
- PostgreSQL
- MinIO / S3
- Structured logging

## Remove

- Redis
- Celery
- Semantic caching
- Elasticsearch / OpenSearch
- JWT Authentication
- Multi-tenant security layers
- OpenTelemetry stack
- Heavy monitoring infrastructure

---

# Infrastructure Changes

## Remove Redis

Reason:
- Added unnecessary complexity
- Increased memory usage
- Minimal real-world performance gain

Delete:
- Redis containers
- Redis env vars
- Redis dependencies
- Cache logic

---

## Remove Semantic Caching

Remove:
- GPTCache
- LiteLLM cache layer
- Query embedding cache

Replace with:
- Faster retrieval
- Better chunking
- Prompt optimization

---

## Remove Celery

Reason:
- Queue orchestration became harder to maintain
- Increased debugging difficulty
- Too many moving parts

Replace with:
- Native FastAPI async processing
- Lightweight background tasks

Delete:
- Celery workers
- Celery Beat
- Task polling APIs
- Queue logic

---

## Remove Elasticsearch / OpenSearch

Reason:
- Heavy RAM usage
- Large Docker footprint
- Extra synchronization complexity

Replace with:
- Pinecone-only retrieval
- Optional lightweight local BM25 fallback

Delete:
- OpenSearch containers
- Sparse indexing logic
- Hybrid async retrieval orchestration

---

## Remove JWT & Multi-Tenancy

Reason:
- Not needed for current scale
- Added frontend/backend complexity
- Slowed development velocity

Delete:
- JWT middleware
- Auth0/OIDC integration
- RBAC
- Tenant routing
- RLS logic

Application will temporarily operate as:
- Single tenant
- Internal/private deployment

---

# Updated Docker Architecture

## Keep Only Essential Services

```yaml
services:
  frontend:
  backend:
  postgres:
  minio:
```

## Remove

```yaml
redis:
elasticsearch:
celery-worker:
celery-beat:
grafana:
prometheus:
loki:
```

---

# Simplified Reliability Strategy

## Keep

- `tenacity` retry logic
- Request timeouts
- Structured logging
- Health endpoints

## Remove

- Circuit breakers
- DLQ systems
- Distributed tracing
- Heavy observability stack

---

# Revised Engineering Philosophy

Previous approach:
> Build enterprise-scale infrastructure first.

New approach:
> Build only what current scale actually requires.

Priorities:
- Simplicity
- Performance
- Maintainability
- Faster iteration
- Better developer experience
- Lower operational overhead

---

# Refactor Phases

## Phase 1 - Infrastructure Cleanup

- Remove Redis
- Remove Celery
- Remove Elasticsearch
- Remove JWT/Auth
- Remove semantic caching
- Simplify Docker Compose

## Phase 2 - Backend Simplification

- Refactor ingestion pipeline
- Remove task polling APIs
- Simplify retrieval flow
- Remove tenant abstractions

## Phase 3 - Performance Optimization

- Optimize Pinecone queries
- Reduce prompt size
- Improve chunking
- Optimize reranker batching
- Improve model loading

## Phase 4 - Stability & DX

- Faster startup times
- Cleaner logs
- Lower RAM usage
- Simpler debugging
- Easier deployment

---

# Final Goal

A lean AI-native platform with:

- Minimal infrastructure
- Faster development
- Better runtime performance
- Simpler operations
- Strong AI capabilities without overengineering
