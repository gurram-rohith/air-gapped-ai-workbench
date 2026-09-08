"""
Document Ingestion & Chunking Module for Air-Gapped AI Workbench.

Loads raw documents (PDF, TXT) from the specified directory, handles
edge cases gracefully (missing or empty folder), and chunks content
using RecursiveCharacterTextSplitter for downstream vector embedding.
"""

import logging
import os
from pathlib import Path
from typing import List, Union

try:
    from langchain_core.documents import Document
except ImportError:
    try:
        from langchain.schema import Document
    except ImportError:
        from langchain.docstore.document import Document

try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader
except ImportError:
    from langchain.document_loaders import PyPDFLoader, TextLoader

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def load_and_chunk_documents(
    docs_dir: Union[str, Path] = "./data/raw_docs",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    Read text (.txt) and PDF (.pdf) files from the specified directory and split them into chunks.

    Args:
        docs_dir (str | Path): Path to raw documents directory (default: "./data/raw_docs").
        chunk_size (int): Maximum size of each text chunk (default: 500).
        chunk_overlap (int): Number of overlapping characters between chunks (default: 50).

    Returns:
        List[Document]: List of chunked Document objects.
    """
    target_dir = Path(docs_dir)

    # Ensure directory exists; create it if missing
    if not target_dir.exists():
        logger.warning(f"Raw documents directory '{target_dir}' does not exist. Creating it.")
        target_dir.mkdir(parents=True, exist_ok=True)
        return []

    # Supported file extensions
    supported_extensions = {".pdf", ".txt"}
    raw_files = [
        f for f in target_dir.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]

    if not raw_files:
        logger.info(f"No supported document files (.pdf, .txt) found in '{target_dir}'.")
        return []

    loaded_documents: List[Document] = []

    for file_path in raw_files:
        suffix = file_path.suffix.lower()
        logger.info(f"Loading document: {file_path.name}")
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
                loaded_documents.extend(docs)
            elif suffix == ".txt":
                # Attempt UTF-8 load with fallback
                try:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    docs = loader.load()
                except UnicodeDecodeError:
                    loader = TextLoader(str(file_path), autodetect_encoding=True)
                    docs = loader.load()
                loaded_documents.extend(docs)
        except Exception as e:
            logger.error(f"Failed to load document '{file_path}': {e}", exc_info=True)

    if not loaded_documents:
        logger.warning(f"No document content could be extracted from '{target_dir}'.")
        return []

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(loaded_documents)
    logger.info(
        f"Ingestion complete: Loaded {len(loaded_documents)} document sections from "
        f"{len(raw_files)} files; produced {len(chunks)} chunks."
    )
    return chunks
