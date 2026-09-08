"""
RAG Pipeline Integration & Verification Demo Script.

Tests end-to-end document ingestion, chunking, ChromaDB vector indexing,
and similarity search with offline Ollama embeddings.
"""

import logging
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path for direct script execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.loader import load_and_chunk_documents
from backend.rag.vector_store import search_similar_documents, store_documents

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger("rag_demo")

SAMPLE_DOCS_DIR = "./data/raw_docs"
SAMPLE_FILE_PATH = os.path.join(SAMPLE_DOCS_DIR, "sample_workbench_overview.txt")

SAMPLE_CONTENT = """# Air-Gapped Agentic AI Workbench Architecture

The Sovereign Air-Gapped Agentic AI Workbench is an offline, multi-agent AI system designed for secure, air-gapped environments without internet access.

## Core Infrastructure
- Host Machine: Dedicated inference workstation powered by NVIDIA RTX 3050 GPU.
- Inference Server: Local Ollama daemon broadcasting at http://192.168.10.190:11434.
- Embeddings Model: nomic-embed-text running locally on the Ollama host.
- Vector Store: ChromaDB persistent vector database located at data/processed_chunks/.
- Backend Gateway: FastAPI powering asynchronous multi-agent orchestration and tool routing.

## Security & Verification
The workbench features a strict Trust Layer providing grounding checks, hallucination reduction, and sandboxed code execution in an isolated subprocessing environment.
"""


def ensure_sample_documents(docs_dir: str = SAMPLE_DOCS_DIR) -> None:
    """
    Ensure raw documents directory exists and contains at least one test document.
    """
    path = Path(docs_dir)
    path.mkdir(parents=True, exist_ok=True)

    existing_files = [
        f for f in path.iterdir()
        if f.is_file() and f.suffix.lower() in {".pdf", ".txt"}
    ]

    if not existing_files:
        logger.info("Directory '%s' is empty. Writing sample test document...", docs_dir)
        with open(SAMPLE_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(SAMPLE_CONTENT.strip())
        logger.info("Sample test document created at: '%s'", SAMPLE_FILE_PATH)
    else:
        logger.info("Found %d existing document(s) in '%s'.", len(existing_files), docs_dir)


def run_pipeline(
    test_query: str = "How is the air-gapped AI workbench configured and what models are used?",
    k: int = 2,
) -> None:
    """
    Execute the RAG pipeline end-to-end:
    1. Ensure sample documents exist in data/raw_docs/
    2. Load and chunk documents
    3. Store chunks in ChromaDB with local Ollama embeddings
    4. Execute similarity search query and display results
    """
    print("\n" + "=" * 70)
    print("🚀 STARTING AIR-GAPPED RAG PIPELINE VERIFICATION")
    print("=" * 70)

    # Step 1: Ensure sample documents
    print("\n[Step 1/4] Checking document directory...")
    ensure_sample_documents(SAMPLE_DOCS_DIR)

    # Step 2: Ingest & Chunk Documents
    print("\n[Step 2/4] Loading and chunking raw documents...")
    try:
        chunks = load_and_chunk_documents(
            docs_dir=SAMPLE_DOCS_DIR,
            chunk_size=500,
            chunk_overlap=50,
        )
        print(f"  ✓ Successfully extracted {len(chunks)} text chunk(s).")
    except Exception as e:
        print(f"  ✗ Failed to load documents: {e}")
        logger.error("Document ingestion failed.", exc_info=True)
        return

    if not chunks:
        print("  ! No document chunks were created. Aborting pipeline test.")
        return

    # Step 3: Embed & Store in ChromaDB
    print("\n[Step 3/4] Storing chunks in ChromaDB with Ollama embeddings...")
    try:
        stored_ids = store_documents(chunks=chunks)
        print(f"  ✓ Successfully indexed {len(stored_ids) if stored_ids else len(chunks)} chunk(s) in ChromaDB.")
    except Exception as e:
        print(f"\n  ✗ Error connecting to Ollama or ChromaDB: {e}")
        print("  ------------------------------------------------------------------")
        print("  [!] DIAGNOSTIC: The host inference server at http://192.168.10.190:11434")
        print("      is currently unreachable or the 'nomic-embed-text' model is missing.")
        print("      Please verify:")
        print("        1. The host machine is online and Ollama is active.")
        print("        2. LAN network connectivity to 192.168.10.190:11434 is open.")
        print("        3. 'ollama pull nomic-embed-text' has been run on the host.")
        print("  ------------------------------------------------------------------")
        return

    # Step 4: Similarity Search Retrieval
    print(f"\n[Step 4/4] Performing similarity search for query:")
    print(f"  Query: \"{test_query}\" (Top-k: {k})")

    try:
        results = search_similar_documents(query=test_query, k=k)
        print(f"\n  ✓ Retrieved {len(results)} matching chunk(s):\n")

        for idx, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "Unknown Source")
            print(f"  --- [Result #{idx}] Source: {source} ---")
            print(f"  {doc.page_content.strip()}")
            print("  " + "-" * 50)

    except Exception as e:
        print(f"  ✗ Failed to execute similarity search: {e}")
        logger.error("Similarity search failed.", exc_info=True)
        return

    print("\n" + "=" * 70)
    print("✅ RAG PIPELINE VERIFICATION COMPLETED SUCCESSFULLY")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    query_arg = sys.argv[1] if len(sys.argv) > 1 else "How is the air-gapped AI workbench configured and what models are used?"
    run_pipeline(test_query=query_arg, k=2)
