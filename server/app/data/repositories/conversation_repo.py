import logging
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from server.app.data.models import Conversation

logger = logging.getLogger("lawyergpt.repo.conversation")


async def create_conversation(db: AsyncSession) -> Conversation:
    conversation = Conversation()
    db.add(conversation)
    await db.flush()
    logger.info("Created conversation id=%s", conversation.id)
    return conversation


async def list_conversations(db: AsyncSession) -> list[Conversation]:
    result = await db.execute(
        select(Conversation).order_by(Conversation.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_conversation(db: AsyncSession, conversation_id: str) -> Conversation | None:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    return result.scalar_one_or_none()


async def update_conversation_title(db: AsyncSession, conversation_id: str, title: str) -> None:
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if conversation:
        conversation.title = title
        await db.flush()
        logger.info("Updated conversation title id=%s title=%s", conversation_id, title)


async def delete_conversation(db: AsyncSession, conversation_id: str) -> bool:
    result = await db.execute(
        delete(Conversation).where(Conversation.id == conversation_id)
    )
    deleted = result.rowcount > 0
    if deleted:
        logger.info("Deleted conversation id=%s", conversation_id)
    return deleted
