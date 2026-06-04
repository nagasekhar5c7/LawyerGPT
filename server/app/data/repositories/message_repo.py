import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.data.models import Message

logger = logging.getLogger("lawyergpt.repo.message")


async def create_message(
    db: AsyncSession,
    conversation_id: str,
    role: str,
    content: str,
    citations: list | None = None,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        citations=citations or [],
    )
    db.add(message)
    await db.flush()
    logger.info("Created message id=%s conv=%s role=%s", message.id, conversation_id, role)
    return message


async def get_messages_by_conversation(
    db: AsyncSession, conversation_id: str
) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())
