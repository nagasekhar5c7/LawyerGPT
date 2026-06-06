"""
PDF Document Loader (Extract phase of ETL pipeline).

Loads PDF files from a directory or a single file path, extracts text content
page by page, and returns LangChain Document objects with metadata
(filename, page_number) preserved for downstream citation tracking.
"""

import logging
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", message=".*langchain-community.*is being sunset.*")

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger("lawyergpt.engine.loader")


def load_pdf(file_path: str | Path) -> list[Document]:
    """Load a single PDF file and return a list of Documents (one per page)."""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    if not file_path.suffix.lower() == ".pdf":
        raise ValueError(f"Expected a PDF file, got: {file_path.suffix}")

    logger.info("Loading PDF: %s", file_path.name)

    loader = PyPDFLoader(str(file_path))
    pages = loader.load()

    documents: list[Document] = []
    for page in pages:
        page.metadata["filename"] = file_path.name
        page.metadata["page_number"] = page.metadata.get("page", 0) + 1
        documents.append(page)

    logger.info(
        "Loaded %d page(s) from %s", len(documents), file_path.name
    )
    return documents


def load_pdfs_from_directory(directory: str | Path) -> list[Document]:
    """Load all PDF files from a directory and return combined Documents."""
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"Not a directory: {directory}")

    pdf_files = sorted(directory.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDF files found in %s", directory)
        return []

    logger.info("Found %d PDF file(s) in %s", len(pdf_files), directory)

    all_documents: list[Document] = []
    for pdf_file in pdf_files:
        try:
            docs = load_pdf(pdf_file)
            all_documents.extend(docs)
        except Exception as e:
            logger.error("Failed to load %s: %s", pdf_file.name, str(e))

    logger.info(
        "Total documents loaded: %d page(s) from %d file(s)",
        len(all_documents),
        len(pdf_files),
    )
    return all_documents


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    target = sys.argv[1] if len(sys.argv) > 1 else "uploads"
    target_path = Path(target)

    if target_path.is_file():
        results = load_pdf(target_path)
    elif target_path.is_dir():
        results = load_pdfs_from_directory(target_path)
    else:
        print(f"Error: '{target}' is not a valid file or directory")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"LOADER RESULTS")
    print(f"{'='*60}")
    print(f"Total pages extracted: {len(results)}")
    print(f"{'='*60}\n")

    for doc in results:
        filename = doc.metadata.get("filename", "unknown")
        page_num = doc.metadata.get("page_number", "?")
        content_preview = doc.page_content[:200].replace("\n", " ")
        print(f"[{filename} | Page {page_num}]")
        print(f"  Content ({len(doc.page_content)} chars): {content_preview}...")
        print(f"  Metadata: {doc.metadata}")
        print()
