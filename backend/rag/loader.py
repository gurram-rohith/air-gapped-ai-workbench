# pyright: reportMissingImports=false, reportGeneralTypeIssues=false
# mypy: ignore-missing-imports
"""
Document Ingestion & Chunking Module for Air-Gapped AI Workbench.

Loads raw documents (PDF, TXT) from the specified directory, handles
edge cases gracefully (missing or empty folder), and chunks content
using RecursiveCharacterTextSplitter for downstream vector embedding.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, List, Union

try:
    from langchain_community.document_loaders import PyPDFLoader, TextLoader  # type: ignore
except ImportError:
    try:
        from langchain.document_loaders import PyPDFLoader, TextLoader  # type: ignore
    except ImportError:
        PyPDFLoader = None  # type: ignore
        TextLoader = None  # type: ignore

try:
    from langchain_core.documents import Document  # type: ignore
except ImportError:
    try:
        from langchain.schema import Document  # type: ignore
    except ImportError:
        try:
            from langchain.docstore.document import Document  # type: ignore
        except ImportError:
            class Document:  # type: ignore
                """Fallback Document container if LangChain is not yet installed."""
                def __init__(self, page_content: str = "", metadata: dict[str, Any] | None = None) -> None:
                    self.page_content = page_content
                    self.metadata = metadata or {}

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter  # type: ignore
except ImportError:
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter  # type: ignore
    except ImportError:
        RecursiveCharacterTextSplitter = None  # type: ignore

logger = logging.getLogger(__name__)

__all__ = ["load_and_chunk_documents", "Document"]


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

    if PyPDFLoader is None or TextLoader is None:
        raise ImportError(
            "LangChain document loaders are not installed. "
            "Please install dependencies via: pip install langchain-community pypdf"
        )

    loaded_documents: List[Document] = []

    for file_path in raw_files:
        suffix = file_path.suffix.lower()
        logger.info("Loading document: %s", file_path.name)
        try:
            if suffix == ".pdf":
                pdf_loader = PyPDFLoader(str(file_path))
                loaded_documents.extend(pdf_loader.load())
            elif suffix == ".txt":
                try:
                    txt_loader = TextLoader(str(file_path), encoding="utf-8")
                    loaded_documents.extend(txt_loader.load())
                except UnicodeDecodeError:
                    txt_loader = TextLoader(str(file_path), autodetect_encoding=True)
                    loaded_documents.extend(txt_loader.load())
        except Exception as exc:
            logger.error("Failed to load document '%s': %s", file_path, exc, exc_info=True)

    if not loaded_documents:
        logger.warning("No document content could be extracted from '%s'.", target_dir)
        return []

    if RecursiveCharacterTextSplitter is None:
        raise ImportError(
            "RecursiveCharacterTextSplitter is not installed. "
            "Please install dependencies via: pip install langchain-text-splitters"
        )

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
