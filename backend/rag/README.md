# 🧠 Air-Gapped RAG (Retrieval-Augmented Generation) Subsystem

> **High-Assurance, 100% Offline Document Parsing, Local Vector Indexing, and Context Retrieval Pipeline**  
> *Sovereign Agentic AI Workbench (SIH 26117)*

---

## 📑 Table of Contents
1. [Architecture Overview](#-architecture-overview)
2. [Data Flow & Lifecycle](#-data-flow--lifecycle)
3. [Component Breakdown & Code Walkthrough](#-component-breakdown--code-walkthrough)
   - [1. `loader.py` — Ingestion & Text Chunking](#1-loaderpy--document-ingestion--chunking)
   - [2. `vector_store.py` — ChromaDB & Local Ollama Embeddings](#2-vector_storepy--persistent-vector-storage)
   - [3. `service.py` — High-Level Interface Layer](#3-servicepy--service-interface-layer)
   - [4. `main.py` — Pipeline Integration & Diagnostic Runner](#4-mainpy--pipeline-integration--verification)
   - [5. `test_service.py` — Automated Sanity Suite](#5-test_servicepy--automated-sanity-test-suite)
   - [6. `__init__.py` — Package Namespace & Public API](#6-__init__py--package-namespace--public-api)
4. [Public API Reference](#-public-api-reference)
5. [Environment & Configuration](#-environment--configuration)
6. [Offline Air-Gapped Guarantees & Security](#-offline-air-gapped-guarantees--security)
7. [Developer Integration & Troubleshooting Guide](#-developer-integration--troubleshooting-guide)

---

## 🏛️ Architecture Overview

The `backend/rag` module provides a decoupled, sovereign retrieval engine tailored for environments completely disconnected from the public internet. It transforms raw unstructured documents (PDF manuals, text policies, operational guides) into high-dimensional semantic vectors stored locally in a persistent ChromaDB database.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                       AIR-GAPPED HOST BOUNDARY                             │
│                                                                            │
│   ┌─────────────────────┐                  ┌───────────────────────────┐   │
│   │   Raw Documents     │                  │  Local Ollama Server      │   │
│   │  (PDF / TXT Files)  │                  │  (http://192.168.10.190)  │   │
│   │   data/raw_docs/    │                  │  Model: nomic-embed-text  │   │
│   └──────────┬──────────┘                  └─────────────▲─────────────┘   │
│              │                                           │                 │
│              ▼                                           │ (LAN Embeddings)│
│   ┌─────────────────────┐                  ┌─────────────┴─────────────┐   │
│   │      loader.py      │                  │      vector_store.py      │   │
│   │  PyPDF / TextLoader │───[Chunks]──────▶│   ChromaDB Persistent DB  │   │
│   │ RecursiveTextSplit  │                  │   data/processed_chunks/  │   │
│   └─────────────────────┘                  └─────────────┬─────────────┘   │
│                                                          │                 │
│                                            (Top-k Semantic Match)          │
│                                                          │                 │
│                                            ┌─────────────▼─────────────┐   │
│                                            │        service.py         │   │
│                                            │ retrieve_context_for_     │   │
│                                            │          prompt()         │   │
│                                            └─────────────┬─────────────┘   │
│                                                          │                 │
└──────────────────────────────────────────────────────────┼─────────────────┘
                                                           │
                   ┌───────────────────────────────────────┴───────────────────────────────────────┐
                   │                                                                               │
        ┌──────────▼──────────┐                                                         ┌──────────▼──────────┐
        │     Developer 2     │                                                         │     Developer 5     │
        │ Core LLM Inference  │                                                         │     Trust Layer     │
        │  (Ollama Prompts)   │                                                         │ (Grounding & Facts) │
        └─────────────────────┘                                                         └─────────────────────┘
```

---

## 🔄 Data Flow & Lifecycle

```
[Raw File: .pdf / .txt]
          │
          ▼
   1. Ingestion: PyPDFLoader / TextLoader loads raw textual streams.
          │
          ▼
   2. Chunking: RecursiveCharacterTextSplitter (chunk_size=500, overlap=50) creates atomic Document segments.
          │
          ▼
   3. Embedding: Document text is batched and sent to Ollama (nomic-embed-text) over LAN.
          │
          ▼
   4. Storage: High-dimensional vectors + metadata persisted into local ChromaDB disk collection.
          │
          ▼
   5. Retrieval: Query vectors computed on-the-fly; top-k cosine similarity matches extracted.
          │
          ▼
   6. Service: Clean list of strings returned to Developer 2 (Inference) and Developer 5 (Trust Layer).
```

---

## 🧩 Component Breakdown & Code Walkthrough

### 1. `loader.py` — Document Ingestion & Chunking
- **Primary Function**: Discovers, reads, and parses `.txt` and `.pdf` files from `./data/raw_docs/`, splitting them into manageable chunks for vector indexing.
- **Key Features**:
  - Auto-provisions directory if missing.
  - Handles `.txt` encoding fallbacks (UTF-8 with automatic character detection fallback).
  - Configurable chunk size and overlap (defaults: `500` characters with `50` character overlap).
  - Pylance type stubs and robust import fallbacks.

```python
# Key Function Signature in loader.py
def load_and_chunk_documents(
    docs_dir: Union[str, Path] = "./data/raw_docs",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    ...
```

---

### 2. `vector_store.py` — Persistent Vector Storage
- **Primary Function**: Interfaces with the local ChromaDB database and Ollama embedding engine.
- **Key Features**:
  - Connects strictly to local offline Ollama host: `http://192.168.10.190:11434` with model `nomic-embed-text`.
  - Persists database to local folder `./data/processed_chunks/`.
  - Zero cloud calls, zero external API keys required.
  - Implements document ingestion (`store_documents`) and semantic similarity search (`search_similar_documents`).

```python
# Key Functions in vector_store.py
def store_documents(
    chunks: List[Document],
    persist_directory: Union[str, Path] = "./data/processed_chunks",
    collection_name: str = "air_gapped_docs",
) -> List[str]:
    ...

def search_similar_documents(
    query: str,
    k: int = 3,
    persist_directory: Union[str, Path] = "./data/processed_chunks",
    collection_name: str = "air_gapped_docs",
) -> List[Document]:
    ...
```

---

### 3. `service.py` — Service Interface Layer
- **Primary Function**: Exposes a clean, decoupled, high-level API for other developers (Inference, Trust Layer, FastAPI routes).
- **Key Features**:
  - Extracts clean text strings (`list[str]`) from raw LangChain `Document` objects.
  - Fault-Tolerant: Catches network disconnects, missing vector collections, or offline hosts gracefully and returns `[]` without raising uncaught exceptions.
  - Includes convenience helper `format_context_for_prompt` for markdown prompt formatting.

```python
# Key Function in service.py
def retrieve_context_for_prompt(user_query: str, top_k: int = 3) -> List[str]:
    ...
```

---

### 4. `main.py` — Pipeline Integration & Verification
- **Primary Function**: End-to-end integration and diagnostics runner.
- **Key Features**:
  - Automatically seeds sample workbench architecture documentation if `data/raw_docs/` is empty.
  - Executes chunking, vector indexing, and test retrieval sequentially.
  - Outputs actionable diagnostic instructions if the LAN inference server is unreachable.

```bash
# Execute End-to-End Verification Pipeline
python backend/rag/main.py "How is the air-gapped workbench configured?"
```

---

### 5. `test_service.py` — Automated Sanity Test Suite
- **Primary Function**: Automated test script to validate zero-crash resilience and typing contracts.
- **Key Features**:
  - Creates a dedicated technical manual `data/raw_docs/sample_manual.txt`.
  - Ingests and stores chunks into ChromaDB.
  - Invokes `retrieve_context_for_prompt` and asserts that returned data is a valid `list[str]`.
  - Proves the service never crashes even under cold start or offline conditions.

```bash
# Run the Sanity Test Suite
python backend/rag/test_service.py
```

---

### 6. `__init__.py` — Package Namespace & Public API
- **Primary Function**: Centralizes public exports so that downstream modules can import everything directly from `backend.rag`.

```python
# Unified Public API in backend/rag/__init__.py
from backend.rag.loader import load_and_chunk_documents
from backend.rag.vector_store import (
    get_embeddings,
    get_vector_store,
    store_documents,
    search_similar_documents,
)
from backend.rag.service import retrieve_context_for_prompt, format_context_for_prompt
from backend.rag.main import run_pipeline

__all__ = [
    "load_and_chunk_documents",
    "get_embeddings",
    "get_vector_store",
    "store_documents",
    "search_similar_documents",
    "retrieve_context_for_prompt",
    "format_context_for_prompt",
    "run_pipeline",
]
```

---

## 💻 Code Quick-Reference

### How Developer 2 (Core LLM) Uses RAG:
```python
from backend.rag import retrieve_context_for_prompt, format_context_for_prompt

def generate_rag_response(user_prompt: str) -> str:
    # 1. Retrieve top-3 context chunks as strings
    contexts = retrieve_context_for_prompt(user_prompt, top_k=3)
    
    # 2. Format into clean prompt section
    context_block = format_context_for_prompt(contexts)
    
    # 3. Assemble final augmented system prompt
    augmented_prompt = f"""
You are an air-gapped sovereign AI assistant. Answer using the provided context.

{context_block}

User Question: {user_prompt}
"""
    return augmented_prompt
```

### How Developer 5 (Trust Layer) Uses RAG:
```python
from backend.rag import retrieve_context_for_prompt

def verify_grounding(claim: str) -> bool:
    # Retrieve closest matching knowledge base sections
    evidence = retrieve_context_for_prompt(claim, top_k=2)
    
    if not evidence:
        return False  # No grounding evidence found
        
    # Perform local NLI / fact check against evidence
    return True
```

---

## ⚙️ Environment & Configuration

All components support dynamic runtime configuration via `.env` or system environment variables:

| Variable | Default Value | Purpose |
| :--- | :--- | :--- |
| `OLLAMA_HOST` | `http://192.168.10.190:11434` | Host LAN IP of Ollama daemon |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Offline vector embedding model |
| `CHROMA_DB_DIR` | `./data/processed_chunks` | Persistent disk directory for ChromaDB |
| `CHROMA_COLLECTION_NAME` | `air_gapped_docs` | Vector collection name |

---

## 🛡️ Offline Air-Gapped Guarantees & Security

1. **No External Network Calls**: Zero calls to `api.openai.com`, `api.anthropic.com`, HuggingFace Hub, or telemetry analytics.
2. **Local Embedding Computation**: Vectors are generated exclusively on the LAN RTX 3050 hardware.
3. **Local Disk Persistence**: Embeddings and documents never leave the local file system boundary (`./data/`).
4. **Resilient Error Trapping**: Unreachable services do not propagate unhandled 500 errors to user sessions.
