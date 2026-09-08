"""
Service Interface Layer for Air-Gapped RAG Module.

Provides a clean, high-level, decoupled interface for downstream modules
(Core LLM Inference, Trust Layer / Grounding, and FastAPI Gateway) to query
retrieved context without needing direct ChromaDB or loader dependencies.
"""

import logging
from typing import List, Optional

from backend.rag.vector_store import search_similar_documents

logger = logging.getLogger(__name__)


def retrieve_context_for_prompt(user_query: str, top_k: int = 3) -> List[str]:
    """
    Retrieve relevant knowledge context strings for a given prompt/query.

    Queries the persistent ChromaDB vector store using local Ollama embeddings
    (nomic-embed-text) and extracts the textual excerpts.

    Args:
        user_query (str): The user's input prompt or question.
        top_k (int): Maximum number of context excerpts to retrieve (default: 3).

    Returns:
        List[str]: List of retrieved text context excerpts. Returns an empty list
                   `[]` if no documents match, ChromaDB is uninitialized, or
                   the local Ollama host is unreachable.

    Example:
        >>> from backend.rag.service import retrieve_context_for_prompt
        >>> contexts = retrieve_context_for_prompt("What is the air-gapped host configuration?", top_k=2)
        >>> print(contexts)
        ['The Sovereign Air-Gapped Agentic AI Workbench...', 'Host Machine: Dedicated...']
    """
    if not user_query or not user_query.strip():
        logger.debug("retrieve_context_for_prompt received an empty query. Returning [].")
        return []

    try:
        # Perform similarity search against ChromaDB
        matched_docs = search_similar_documents(query=user_query.strip(), k=top_k)

        if not matched_docs:
            logger.info(f"No matching documents retrieved for query: '{user_query[:40]}...'")
            return []

        # Extract textual content from document objects
        context_excerpts = [
            doc.page_content.strip()
            for doc in matched_docs
            if doc.page_content and doc.page_content.strip()
        ]

        logger.info(
            f"Successfully retrieved {len(context_excerpts)} context chunk(s) for query: '{user_query[:40]}...'"
        )
        return context_excerpts

    except Exception as exc:
        # Gracefully swallow connection/indexing errors and return empty list
        logger.warning(
            f"Gracefully caught exception during context retrieval for '{user_query[:40]}...': {exc}"
        )
        return []


def format_context_for_prompt(context_chunks: List[str], prefix: str = "Relevant Context:\n") -> str:
    """
    Convenience helper to format a list of context strings into a prompt-ready markdown block.

    Args:
        context_chunks (List[str]): List of context strings.
        prefix (str): Header prefix for the context block.

    Returns:
        str: Formatted context block, or empty string if context_chunks is empty.
    """
    if not context_chunks:
        return ""

    formatted_sections = [
        f"[{idx}] {chunk}" for idx, chunk in enumerate(context_chunks, 1)
    ]
    return f"{prefix}" + "\n\n".join(formatted_sections)
