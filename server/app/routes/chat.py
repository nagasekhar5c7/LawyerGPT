import logging
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from server.app.data.database import get_db
from server.app.data.repositories import conversation_repo
from server.app.schemas.chat import ChatRequest
from server.app.services import chat_service
from server.app.exceptions import ConversationNotFoundError

logger = logging.getLogger("lawyergpt.routes.chat")
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/{conversation_id}")
async def chat(
    conversation_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    logger.info("POST /api/v1/chat/%s model=%s", conversation_id, request.model)

    conversation = await conversation_repo.get_conversation(db, conversation_id)
    if not conversation:
        raise ConversationNotFoundError(conversation_id)
   
    return EventSourceResponse(
        chat_service.process_chat(db, conversation_id, request.message, request.model),
        media_type="text/event-stream",
    )
