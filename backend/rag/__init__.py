"""
RAG (Retrieval-Augmented Generation) package for Air-Gapped AI Workbench.
"""

from backend.rag.loader import load_and_chunk_documents
from backend.rag.main import run_pipeline
from backend.rag.vector_store import (
    get_embeddings,
    get_vector_store,
    search_similar_documents,
    store_documents,
)

__all__ = [
    "load_and_chunk_documents",
    "get_embeddings",
    "get_vector_store",
    "store_documents",
    "search_similar_documents",
    "run_pipeline",
]
