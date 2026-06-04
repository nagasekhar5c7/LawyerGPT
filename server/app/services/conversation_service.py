import logging
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.data.repositories import conversation_repo
from server.app.data.models import Conversation
from server.app.exceptions import ConversationNotFoundError

logger = logging.getLogger("lawyergpt.service.conversation")


async def create(db: AsyncSession) -> Conversation:
    logger.info("Creating new conversation")
    return await conversation_repo.create_conversation(db)


async def list_all(db: AsyncSession) -> list[Conversation]:
    logger.info("Listing all conversations")
    return await conversation_repo.list_conversations(db)


async def get_by_id(db: AsyncSession, conversation_id: str) -> Conversation:
    logger.info("Fetching conversation id=%s", conversation_id)
    conversation = await conversation_repo.get_conversation(db, conversation_id)
    if not conversation:
        raise ConversationNotFoundError(conversation_id)
    return conversation


async def remove(db: AsyncSession, conversation_id: str) -> None:
    logger.info("Deleting conversation id=%s", conversation_id)
    deleted = await conversation_repo.delete_conversation(db, conversation_id)
    if not deleted:
        raise ConversationNotFoundError(conversation_id)
