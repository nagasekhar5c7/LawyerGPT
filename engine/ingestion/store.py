"""
Vector Store Loader (Load phase of ETL pipeline).

Takes embedded document chunks from the embedder and loads them into
ChromaDB in batches. Uses persistent local storage so vectors survive
across server restarts.
"""

import logging
import os
import uuid
from dotenv import load_dotenv
import chromadb

load_dotenv()

logger = logging.getLogger("lawyergpt.engine.store")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "legal_documents")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "100"))


def get_chroma_client() -> chromadb.ClientAPI:
    """Create and return a persistent ChromaDB client."""
    logger.info("Connecting to ChromaDB at %s", CHROMA_PERSIST_DIR)
    return chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)


def get_or_create_collection(
    client: chromadb.ClientAPI,
    collection_name: str = CHROMA_COLLECTION_NAME,
) -> chromadb.Collection:
    """Get or create a ChromaDB collection."""
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "LawyerGPT legal document embeddings"},
    )
    logger.info(
        "Collection '%s' ready (existing count: %d)",
        collection_name,
        collection.count(),
    )
    return collection


def store_embeddings(
    embedded_chunks: list[dict],
    collection_name: str = CHROMA_COLLECTION_NAME,
    batch_size: int = BATCH_SIZE,
) -> int:
    """
    Load embedded chunks into ChromaDB in batches.

    Args:
        embedded_chunks: List of dicts from embedder, each with:
            - content: str (chunk text)
            - embedding: list[float] (vector)
            - metadata: dict (filename, page_number, chunk_index, etc.)
        collection_name: ChromaDB collection name
        batch_size: Number of vectors per batch insert

    Returns:
        Total number of vectors stored
    """
    if not embedded_chunks:
        logger.warning("No embedded chunks to store")
        return 0

    client = get_chroma_client()
    collection = get_or_create_collection(client, collection_name)

    total_stored = 0
    total_batches = (len(embedded_chunks) + batch_size - 1) // batch_size

    logger.info(
        "Storing %d vector(s) in '%s' (batch_size=%d, total_batches=%d)",
        len(embedded_chunks),
        collection_name,
        batch_size,
        total_batches,
    )

    for i in range(0, len(embedded_chunks), batch_size):
        batch = embedded_chunks[i : i + batch_size]
        batch_num = (i // batch_size) + 1

        ids = [str(uuid.uuid4()) for _ in batch]
        documents = [item["content"] for item in batch]
        embeddings = [item["embedding"] for item in batch]

        metadatas = []
        for item in batch:
            meta = {}
            for key, value in item["metadata"].items():
                if isinstance(value, (str, int, float, bool)):
                    meta[key] = value
                else:
                    meta[key] = str(value)
            metadatas.append(meta)

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        total_stored += len(batch)
        logger.info(
            "Batch %d/%d stored (%d vectors)", batch_num, total_batches, len(batch)
        )

    logger.info(
        "Store complete: %d vector(s) in collection '%s' (total in collection: %d)",
        total_stored,
        collection_name,
        collection.count(),
    )
    return total_stored


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    from engine.ingestion.loader import load_pdf, load_pdfs_from_directory
    from engine.ingestion.chunker import chunk_documents
    from engine.ingestion.embedder import embed_documents
    from pathlib import Path

    target = sys.argv[1] if len(sys.argv) > 1 else "uploads"
    target_path = Path(target)

    if target_path.is_file():
        documents = load_pdf(target_path)
    elif target_path.is_dir():
        documents = load_pdfs_from_directory(target_path)
    else:
        print(f"Error: '{target}' is not a valid file or directory")
        sys.exit(1)

    chunks = chunk_documents(documents)
    embedded = embed_documents(chunks)
    stored = store_embeddings(embedded)

    client = get_chroma_client()
    collection = get_or_create_collection(client)

    print(f"\n{'='*60}")
    print(f"STORE RESULTS")
    print(f"{'='*60}")
    print(f"Input pages:          {len(documents)}")
    print(f"Chunks created:       {len(chunks)}")
    print(f"Vectors embedded:     {len(embedded)}")
    print(f"Vectors stored:       {stored}")
    print(f"Collection:           {CHROMA_COLLECTION_NAME}")
    print(f"Total in collection:  {collection.count()}")
    print(f"Persist directory:    {CHROMA_PERSIST_DIR}")
    print(f"{'='*60}\n")

    sample = collection.peek(limit=3)
    if sample["ids"]:
        print("Sample entries from ChromaDB:")
        for i, doc_id in enumerate(sample["ids"]):
            meta = sample["metadatas"][i] if sample["metadatas"] else {}
            doc_preview = (sample["documents"][i] or "")[:80]
            print(f"  [{doc_id[:8]}...] {meta.get('filename', '?')} p.{meta.get('page_number', '?')} chunk={meta.get('chunk_index', '?')}")
            print(f"    \"{doc_preview}...\"")
            print()
