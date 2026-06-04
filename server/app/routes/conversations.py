import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.data.database import get_db
from server.app.services import conversation_service
from server.app.schemas.conversation import ConversationResponse, ConversationWithMessagesResponse

logger = logging.getLogger("lawyergpt.routes.conversations")
router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(db: AsyncSession = Depends(get_db)):
    logger.info("POST /api/v1/conversations")
    conversation = await conversation_service.create(db)
    return conversation


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(db: AsyncSession = Depends(get_db)):
    logger.info("GET /api/v1/conversations")
    return await conversation_service.list_all(db)


@router.get("/{conversation_id}", response_model=ConversationWithMessagesResponse)
async def get_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("GET /api/v1/conversations/%s", conversation_id)
    return await conversation_service.get_by_id(db, conversation_id)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str, db: AsyncSession = Depends(get_db)):
    logger.info("DELETE /api/v1/conversations/%s", conversation_id)
    await conversation_service.remove(db, conversation_id)
