"""
Document Ingestion & Chunking Module for Air-Gapped AI Workbench.

Loads raw documents (PDF, TXT) from the specified directory, handles
edge cases gracefully (missing or empty folder), and chunks content
using RecursiveCharacterTextSplitter for downstream vector embedding.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Union

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

__all__ = ["load_and_chunk_documents"]


def load_and_chunk_documents(
    docs_dir: Union[str, Path] = "./data/raw_docs",
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> List[Document]:
    """
    Read text (.txt) and PDF (.pdf) files from the specified directory and split them into chunks.

    Args:
        docs_dir (Union[str, Path]): Path to raw documents directory (default: "./data/raw_docs").
        chunk_size (int): Maximum size of each text chunk (default: 500).
        chunk_overlap (int): Number of overlapping characters between chunks (default: 50).

    Returns:
        List[Document]: List of chunked Document objects.
    """
    target_dir = Path(docs_dir)

    # Ensure directory exists; create it if missing
    if not target_dir.exists():
        logger.warning("Raw documents directory '%s' does not exist. Creating it.", target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        return []

    # Supported file extensions
    supported_extensions = {".pdf", ".txt"}
    raw_files = [
        f for f in target_dir.iterdir()
        if f.is_file() and f.suffix.lower() in supported_extensions
    ]

    if not raw_files:
        logger.info("No supported document files (.pdf, .txt) found in '%s'.", target_dir)
        return []

    loaded_documents: List[Document] = []

    for file_path in raw_files:
        suffix = file_path.suffix.lower()
        logger.info("Loading document: %s", file_path.name)
        try:
            if suffix == ".pdf":
                pdf_loader = PyPDFLoader(file_path=str(file_path))
                loaded_documents.extend(pdf_loader.load())
            elif suffix == ".txt":
                try:
                    txt_loader = TextLoader(file_path=str(file_path), encoding="utf-8")
                    loaded_documents.extend(txt_loader.load())
                except UnicodeDecodeError:
                    txt_loader = TextLoader(file_path=str(file_path), autodetect_encoding=True)
                    loaded_documents.extend(txt_loader.load())
        except Exception as exc:
            logger.error("Failed to load document '%s': %s", file_path, exc, exc_info=True)

    if not loaded_documents:
        logger.warning("No document content could be extracted from '%s'.", target_dir)
        return []

    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = text_splitter.split_documents(loaded_documents)
    logger.info(
        "Ingestion complete: Loaded %d document sections from %d files; produced %d chunks.",
        len(loaded_documents),
        len(raw_files),
        len(chunks),
    )
    return chunks
