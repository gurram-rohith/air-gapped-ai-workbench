"""
Vector Store and Retrieval Module for Air-Gapped AI Workbench.

Provides persistent vector indexing and similarity search using ChromaDB
and local Ollama embeddings (nomic-embed-text) running strictly offline.
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Union

try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        from langchain.docstore.document import Document

try:
    from langchain_ollama import OllamaEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import OllamaEmbeddings
    except ImportError:
        from langchain.embeddings import OllamaEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    try:
        from langchain_community.vectorstores import Chroma
    except ImportError:
        from langchain.vectorstores import Chroma

logger = logging.getLogger(__name__)

# Default offline environment configuration
DEFAULT_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://192.168.10.190:11434")
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
DEFAULT_CHROMA_DIR = os.getenv("CHROMA_DB_DIR", "./data/processed_chunks")
DEFAULT_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "air_gapped_docs")


def get_embeddings(
    base_url: str = DEFAULT_OLLAMA_HOST,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> OllamaEmbeddings:
    """
    Initialize and return strictly local offline OllamaEmbeddings instance.

    Args:
        base_url (str): Local Ollama server URL.
        model (str): Name of the embedding model (default: 'nomic-embed-text').

    Returns:
        OllamaEmbeddings: Configured embedding model client.
    """
    return OllamaEmbeddings(
        base_url=base_url,
        model=model,
    )


def get_vector_store(
    persist_directory: Union[str, Path] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    base_url: str = DEFAULT_OLLAMA_HOST,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> Chroma:
    """
    Initialize and return a persistent Chroma vector store instance.

    Args:
        persist_directory (str | Path): Local storage directory for Chroma database.
        collection_name (str): Name of the collection.
        base_url (str): Local Ollama server URL.
        model (str): Name of the embedding model.

    Returns:
        Chroma: Configured persistent vector store.
    """
    persist_dir_path = Path(persist_directory)
    persist_dir_path.mkdir(parents=True, exist_ok=True)

    embeddings = get_embeddings(base_url=base_url, model=model)

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_dir_path),
    )


def store_documents(
    chunks: List[Document],
    persist_directory: Union[str, Path] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    base_url: str = DEFAULT_OLLAMA_HOST,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> List[str]:
    """
    Add document chunks to the persistent ChromaDB collection.

    Args:
        chunks (List[Document]): List of document chunks to embed and store.
        persist_directory (str | Path): Path to persistent storage directory.
        collection_name (str): Collection name in ChromaDB.
        base_url (str): Local Ollama server URL.
        model (str): Name of the embedding model.

    Returns:
        List[str]: List of document IDs added to the vector store.
    """
    if not chunks:
        logger.warning("No document chunks provided to store_documents(). Skipping.")
        return []

    logger.info(f"Storing {len(chunks)} chunks into ChromaDB at '{persist_directory}'...")
    vector_store = get_vector_store(
        persist_directory=persist_directory,
        collection_name=collection_name,
        base_url=base_url,
        model=model,
    )

    ids = vector_store.add_documents(documents=chunks)

    # Persist if supported by older Chroma client versions
    if hasattr(vector_store, "persist") and callable(getattr(vector_store, "persist")):
        try:
            vector_store.persist()
        except Exception:
            pass

    logger.info(f"Successfully stored {len(ids) if ids else len(chunks)} document chunks in ChromaDB.")
    return ids if ids else []


def search_similar_documents(
    query: str,
    k: int = 3,
    persist_directory: Union[str, Path] = DEFAULT_CHROMA_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    base_url: str = DEFAULT_OLLAMA_HOST,
    model: str = DEFAULT_EMBEDDING_MODEL,
) -> List[Document]:
    """
    Perform similarity search to retrieve top-k matching document chunks.

    Args:
        query (str): The search query or question.
        k (int): Number of top matching document chunks to return (default: 3).
        persist_directory (str | Path): Path to persistent ChromaDB storage directory.
        collection_name (str): Collection name in ChromaDB.
        base_url (str): Local Ollama server URL.
        model (str): Name of the embedding model.

    Returns:
        List[Document]: Top-k most relevant document chunks.
    """
    if not query or not query.strip():
        logger.warning("Empty query provided to search_similar_documents().")
        return []

    persist_dir_path = Path(persist_directory)
    if not persist_dir_path.exists():
        logger.warning(f"ChromaDB directory '{persist_directory}' does not exist yet. Returning empty results.")
        return []

    try:
        vector_store = get_vector_store(
            persist_directory=persist_directory,
            collection_name=collection_name,
            base_url=base_url,
            model=model,
        )

        results = vector_store.similarity_search(query=query, k=k)
        logger.info(f"Retrieved {len(results)} relevant chunks for query: '{query[:50]}...'")
        return results
    except Exception as e:
        logger.error(f"Error executing similarity search: {e}", exc_info=True)
        return []
