"""
Retriever (first step of Query Orchestration pipeline).

Takes a user query, embeds it using the same embedding model used during
ingestion, and performs a similarity search against ChromaDB to return
the top-k most relevant chunks with their metadata for citation tracking.
"""

import logging
import os
from dotenv import load_dotenv
import chromadb
from langchain_openai import OpenAIEmbeddings

load_dotenv()

logger = logging.getLogger("lawyergpt.engine.retriever")

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "legal_documents")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
RETRIEVAL_TOP_K = int(os.getenv("RETRIEVAL_TOP_K", "5"))


def retrieve(
    query: str,
    top_k: int = RETRIEVAL_TOP_K,
    collection_name: str = CHROMA_COLLECTION_NAME,
) -> list[dict]:
    """
    Retrieve the most relevant chunks for a user query.

    Args:
        query: The user's legal question
        top_k: Number of top chunks to retrieve
        collection_name: ChromaDB collection to search

    Returns:
        List of dicts, each containing:
          - content: the chunk text
          - metadata: dict with filename, page_number, chunk_index, etc.
          - distance: similarity distance score (lower = more relevant)
    """
    if not query.strip():
        logger.warning("Empty query provided")
        return []

    logger.info("Retrieving top %d chunks for query: '%s'", top_k, query[:80])

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set")

    embedding_fn = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=api_key)
    query_embedding = embedding_fn.embed_query(query)

    logger.info("Query embedded (%d dimensions)", len(query_embedding))

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_collection(name=collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved: list[dict] = []
    for i in range(len(results["ids"][0])):
        retrieved.append({
            "content": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            "distance": results["distances"][0][i],
        })

    logger.info("Retrieved %d chunk(s)", len(retrieved))
    return retrieved


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is tort law?"

    results = retrieve(query)

    print(f"\n{'='*60}")
    print(f"RETRIEVER RESULTS")
    print(f"{'='*60}")
    print(f"Query:      \"{query}\"")
    print(f"Top-K:      {RETRIEVAL_TOP_K}")
    print(f"Collection: {CHROMA_COLLECTION_NAME}")
    print(f"Results:    {len(results)}")
    print(f"{'='*60}\n")

    for i, r in enumerate(results, 1):
        filename = r["metadata"].get("filename", "unknown")
        page_num = r["metadata"].get("page_number", "?")
        chunk_idx = r["metadata"].get("chunk_index", "?")
        distance = r["distance"]
        content = r["content"].replace("\n", " ")

        print(f"--- Result {i} (distance: {distance:.4f}) ---")
        print(f"  Source:  {filename}, Page {page_num}, Chunk {chunk_idx}")
        print(f"  Content: {content}")
        print()
