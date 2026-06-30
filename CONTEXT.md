# Domain Glossary

Shared vocabulary for the agentic RAG chatbot. Architecture terms (module,
interface, depth, seam, adapter, leverage, locality) follow the `codebase-design`
skill; the terms below name this project's deepened modules.

## Resources

`backend/app/core/dependencies.py`. The single deep module that owns the
lazily-loaded retrieval machinery — embedding model, reranker, and Pinecone
vector store — behind a small interface (`vector_store()`, `reranker()`,
`embedding_model()`, `reset()`, `clear_knowledge_base()`, `status()`). Heavy
models load on first access and are cached. The vector store **is** the
knowledge base: `clear_knowledge_base()` wipes the Pinecone index and drops the
cache; `reset()` drops only the cache so the next access reloads (used after
ingestion). `status()` reports readiness without forcing a load.

Seam: endpoints receive it via `Depends(get_resources)`; the background
ingestion task imports the `resources` singleton directly. Tests swap a fake
through `app.dependency_overrides`.

## DocumentStore

`backend/app/services/document_store.py`. The seam for blob storage of uploaded
files, behind `put` / `get` / `clear`. Two adapters: `S3DocumentStore` (S3/MinIO,
prod) and `InMemoryDocumentStore` (tests). The S3 adapter resolves its client and
bucket lazily on first use, keeping import time free of env reads and network.

Seam: the upload endpoint receives it via `Depends(get_document_store)`; the
background ingestion task imports the `document_store` singleton directly.
