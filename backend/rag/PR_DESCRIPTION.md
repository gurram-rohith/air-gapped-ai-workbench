# Pull Request: RAG Ingestion Pipeline, ChromaDB Vector Store & Service Interface Layer

## 📌 Feature Summary

This PR completes the end-to-end **Retrieval-Augmented Generation (RAG) Pipeline** for Developer 3 on the Sovereign Air-Gapped Agentic AI Workbench. The system operates strictly offline on local hardware, using the host Ollama inference server (`http://192.168.10.190:11434`) and local ChromaDB persistence.

### Key Components Implemented:
1. **Document Ingestion (`backend/rag/loader.py`)**:
   - Ingests raw `.txt` (with UTF-8 and auto-encoding fallback) and `.pdf` files (via `PyPDFLoader`).
   - Recursively splits documents into semantic chunks using `RecursiveCharacterTextSplitter` (`chunk_size=500`, `chunk_overlap=50`).
   - Gracefully handles empty or missing `./data/raw_docs/` directories by auto-creating them without crashing.

2. **ChromaDB Vector Store (`backend/rag/vector_store.py`)**:
   - Integrates local `OllamaEmbeddings` using `nomic-embed-text` hosted at `http://192.168.10.190:11434`.
   - Persists vector embeddings locally under `./data/processed_chunks/`.
   - Exposes `store_documents(chunks)` and `search_similar_documents(query, k=3)`.
   - Zero reliance on cloud or external API endpoints.

3. **Service Interface Layer (`backend/rag/service.py`)**:
   - Decoupled, high-level API wrapper for downstream consumers (Developer 2 - Core LLM / Prompt Engine, Developer 5 - Grounding / Trust Layer, Developer 1 - FastAPI Gateway).
   - Extracts clean text excerpts from ChromaDB and safely returns `list[str]`.
   - Handles uninitialized vector stores and host network interruptions gracefully by returning empty lists `[]` rather than throwing uncaught exceptions.

4. **Sanity Verification & Testing (`backend/rag/test_service.py` & `backend/rag/main.py`)**:
   - Standalone scripts to test the pipeline end-to-end from ingestion to vector search and text retrieval.

---

## 🔌 Exposed Function API (For Developer 2 & Developer 5)

Downstream modules can import the high-level retrieval function directly from the `backend.rag` package:

```python
from backend.rag import retrieve_context_for_prompt

# Retrieve top-k relevant text excerpts as a list of strings
context_chunks: list[str] = retrieve_context_for_prompt(
    user_query="What are the air-gapped workbench security rules?",
    top_k=3
)

# Example output:
# [
#   "The Sovereign AI Workbench operates in a strict air-gapped environment...",
#   "All inference and text embeddings are executed locally on dedicated RTX 3050 hardware..."
# ]
```

### Optional Prompt Formatting Helper:
```python
from backend.rag import format_context_for_prompt

# Converts list of strings into a markdown-formatted prompt block
formatted_block: str = format_context_for_prompt(context_chunks)
```

---

## 📦 Required Dependencies

Add the following packages to the project's Python environment:

```txt
langchain-community
langchain-core
langchain-text-splitters
langchain-ollama
langchain-chroma
chromadb
pypdf
httpx
```

---

## 🧪 Verification & Testing

The implementation was validated using the following test cases in `backend/rag/test_service.py` and `backend/rag/main.py`:

- [x] **Automatic Directory Provisioning**: Verified that `./data/raw_docs/` and `./data/processed_chunks/` are created automatically if missing.
- [x] **Chunk Extraction**: Validated that `load_and_chunk_documents()` successfully extracts chunks with metadata tracking (`source`, `page`).
- [x] **ChromaDB Local Persistence**: Confirmed persistent database creation under `data/processed_chunks/`.
- [x] **Vector Similarity Retrieval**: Confirmed top-$k$ semantic matching against user queries.
- [x] **Fault Tolerance**: Verified that host connection drops or missing vector stores return empty lists `[]` without raising unhandled exceptions.

### Sanity Test Command:
```bash
python backend/rag/test_service.py
```
