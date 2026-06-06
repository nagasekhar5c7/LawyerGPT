"""
Embedding Generator (Transform phase of ETL pipeline).

Takes chunked Document objects and generates vector embeddings using
OpenAI's text-embedding-3-large model. Processes embeddings in batches
for efficiency.
"""

import logging
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()

logger = logging.getLogger("lawyergpt.engine.embedder")

EMBEDDING_MODEL = "text-embedding-3-large"
BATCH_SIZE = 100


def get_embedding_function(model: str = EMBEDDING_MODEL) -> OpenAIEmbeddings:
    """Create and return an OpenAI embedding function."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    return OpenAIEmbeddings(model=model, openai_api_key=api_key)


def embed_documents(
    chunks: list[Document],
    model: str = EMBEDDING_MODEL,
    batch_size: int = BATCH_SIZE,
) -> list[dict]:
    """
    Generate embeddings for a list of document chunks.

    Returns a list of dicts, each containing:
      - content: the chunk text
      - embedding: the vector (list of floats)
      - metadata: the chunk metadata
    """
    if not chunks:
        logger.warning("No chunks provided for embedding")
        return []

    embedding_fn = get_embedding_function(model)
    texts = [chunk.page_content for chunk in chunks]

    logger.info(
        "Embedding %d chunk(s) with model=%s batch_size=%d",
        len(texts),
        model,
        batch_size,
    )

    all_embeddings: list[list[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(texts) + batch_size - 1) // batch_size

        logger.info("Processing batch %d/%d (%d chunks)", batch_num, total_batches, len(batch))
        batch_embeddings = embedding_fn.embed_documents(batch)
        all_embeddings.extend(batch_embeddings)

    results = []
    for chunk, embedding in zip(chunks, all_embeddings):
        results.append({
            "content": chunk.page_content,
            "embedding": embedding,
            "metadata": chunk.metadata,
        })

    logger.info(
        "Embedding complete: %d chunk(s), dimensions=%d",
        len(results),
        len(results[0]["embedding"]) if results else 0,
    )
    return results


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    from engine.ingestion.loader import load_pdf, load_pdfs_from_directory
    from engine.ingestion.chunker import chunk_documents
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

    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    print(f"\n{'='*60}")
    print(f"EMBEDDER {'RESULTS' if api_key else 'DRY RUN (no OPENAI_API_KEY set)'}")
    print(f"{'='*60}")
    print(f"Input chunks:    {len(chunks)}")
    print(f"Embedding model: {EMBEDDING_MODEL}")
    print(f"Batch size:      {BATCH_SIZE}")

    if not api_key:
        print(f"\nNo OPENAI_API_KEY found — showing chunks that would be embedded:\n")
        for chunk in chunks:
            filename = chunk.metadata.get("filename", "unknown")
            page_num = chunk.metadata.get("page_number", "?")
            chunk_idx = chunk.metadata.get("chunk_index", "?")
            preview = chunk.page_content[:100].replace("\n", " ")
            print(f"  [Chunk {chunk_idx} | {filename} | Page {page_num}] {len(chunk.page_content)} chars")
            print(f"    {preview}...")

        print(f"\nTo run with real embeddings:")
        print(f"  export OPENAI_API_KEY=sk-...")
        print(f"  uv run python -m engine.ingestion.embedder {target}")
    else:
        results = embed_documents(chunks)
        print(f"Output vectors:  {len(results)}")
        if results:
            print(f"Dimensions:      {len(results[0]['embedding'])}")
        print(f"{'='*60}\n")

        for r in results:
            filename = r["metadata"].get("filename", "unknown")
            page_num = r["metadata"].get("page_number", "?")
            chunk_idx = r["metadata"].get("chunk_index", "?")
            vec_preview = str(r["embedding"][:5])[:-1] + ", ...]"
            print(f"[Chunk {chunk_idx} | {filename} | Page {page_num}]")
            print(f"  Content: {len(r['content'])} chars")
            print(f"  Vector:  {len(r['embedding'])} dims -> {vec_preview}")
            print()
