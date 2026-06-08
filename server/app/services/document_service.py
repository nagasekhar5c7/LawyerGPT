import logging
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from server.app.config import settings
from server.app.data.models import Document
from server.app.exceptions import DocumentProcessingError

from engine.ingestion.loader import load_pdf
from engine.ingestion.chunker import chunk_documents
from engine.ingestion.embedder import embed_documents
from engine.ingestion.store import store_embeddings

logger = logging.getLogger("lawyergpt.service.document")


async def upload_and_ingest(db: AsyncSession, file: UploadFile) -> Document:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise DocumentProcessingError("Only PDF files are accepted")

    logger.info("Uploading document filename=%s", file.filename)

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / file.filename
    content = await file.read()
    file_size = len(content)

    with open(file_path, "wb") as f:
        f.write(content)

    logger.info("Saved file to %s size=%d bytes", file_path, file_size)

    document = Document(
        filename=file.filename,
        file_size=file_size,
        total_chunks=0,
        status="processing",
    )
    db.add(document)
    await db.flush()

    try:
        logger.info("Starting ingestion pipeline for %s", file.filename)

        pages = load_pdf(str(file_path))
        logger.info("Extracted %d page(s)", len(pages))

        chunks = chunk_documents(pages)
        logger.info("Created %d chunk(s)", len(chunks))

        embedded = embed_documents(chunks)
        logger.info("Generated %d embedding(s)", len(embedded))

        stored = store_embeddings(embedded)
        logger.info("Stored %d vector(s) in ChromaDB", stored)

        document.status = "completed"
        document.total_chunks = stored
        await db.flush()

        logger.info(
            "Ingestion complete id=%s filename=%s chunks=%d",
            document.id, file.filename, stored,
        )

    except Exception as e:
        logger.error("Ingestion failed for %s: %s", file.filename, str(e))
        document.status = "failed"
        await db.flush()
        raise DocumentProcessingError(f"Ingestion failed: {str(e)}")

    return document


async def list_all(db: AsyncSession) -> list[Document]:
    from sqlalchemy import select
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())
