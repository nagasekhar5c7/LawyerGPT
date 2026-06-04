import logging
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.data.database import get_db
from server.app.services import document_service
from server.app.schemas.document import DocumentResponse

logger = logging.getLogger("lawyergpt.routes.documents")
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    logger.info("POST /api/v1/documents/upload filename=%s", file.filename)
    return await document_service.upload_and_ingest(db, file)


@router.get("", response_model=list[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db)):
    logger.info("GET /api/v1/documents")
    return await document_service.list_all(db)
