"""
Text Chunker (Transform phase of ETL pipeline).

Takes Document objects from the loader and splits them into smaller chunks
using LangChain's RecursiveCharacterTextSplitter. Preserves all metadata
from the source documents and adds a chunk_index for ordering.
"""

import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

logger = logging.getLogger("lawyergpt.engine.chunker")

CHUNK_SIZE = 100
CHUNK_OVERLAP = 20


def chunk_documents(
    documents: list[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Document]:
    """Split documents into smaller chunks using recursive character splitting."""

    if not documents:
        logger.warning("No documents provided for chunking")
        return []

    logger.info(
        "Chunking %d document(s) (chunk_size=%d, overlap=%d)",
        len(documents),
        chunk_size,
        chunk_overlap,
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: list[Document] = []
    chunk_index = 0

    for doc in documents:
        splits = splitter.split_documents([doc])

        for split in splits:
            split.metadata["chunk_index"] = chunk_index
            chunks.append(split)
            chunk_index += 1

    logger.info(
        "Chunking complete: %d document(s) -> %d chunk(s)",
        len(documents),
        len(chunks),
    )
    return chunks


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    from engine.ingestion.loader import load_pdf, load_pdfs_from_directory
    from pathlib import Path

    target = sys.argv[1] if len(sys.argv) > 1 else "docs"
    target_path = Path(target)

    if target_path.is_file():
        documents = load_pdf(target_path)
    elif target_path.is_dir():
        documents = load_pdfs_from_directory(target_path)
    else:
        print(f"Error: '{target}' is not a valid file or directory")
        sys.exit(1)

    chunks = chunk_documents(documents)

    print(f"\n{'='*60}")
    print(f"CHUNKER RESULTS")
    print(f"{'='*60}")
    print(f"Input documents (pages): {len(documents)}")
    print(f"Output chunks:           {len(chunks)}")
    print(f"Chunk size:              {CHUNK_SIZE}")
    print(f"Chunk overlap:           {CHUNK_OVERLAP}")
    print(f"{'='*60}\n")

    for chunk in chunks:
        filename = chunk.metadata.get("filename", "unknown")
        page_num = chunk.metadata.get("page_number", "?")
        chunk_idx = chunk.metadata.get("chunk_index", "?")
        content_preview = chunk.page_content[:150].replace("\n", " ")
        print(f"[Chunk {chunk_idx} | {filename} | Page {page_num}]")
        print(f"  Length: {len(chunk.page_content)} chars")
        print(f"  Preview: {content_preview}...")
        print()
