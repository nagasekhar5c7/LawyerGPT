import logging
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile
from server.app.config import settings
from server.app.data.models import Document
from server.app.exceptions import DocumentProcessingError

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

    # Placeholder: the engine ingestion pipeline will process the PDF here
    # For now, mark as completed with 0 chunks
    document.status = "completed"
    document.total_chunks = 0
    await db.flush()

    logger.info("Document ingested id=%s filename=%s status=%s", document.id, file.filename, document.status)
    return document


async def list_all(db: AsyncSession) -> list[Document]:
    from sqlalchemy import select
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())
