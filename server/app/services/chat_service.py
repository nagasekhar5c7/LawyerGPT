import json
import logging
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.data.repositories import conversation_repo, message_repo
from server.app.exceptions import ConversationNotFoundError

logger = logging.getLogger("lawyergpt.service.chat")


async def process_chat(
    db: AsyncSession,
    conversation_id: str,
    user_message: str,
    model: str,
) -> AsyncGenerator[str, None]:
    logger.info("Processing chat conv=%s model=%s", conversation_id, model)

    conversation = await conversation_repo.get_conversation(db, conversation_id)
    if not conversation:
        raise ConversationNotFoundError(conversation_id)

    await message_repo.create_message(db, conversation_id, "user", user_message)

    if conversation.title == "New Chat":
        title = user_message[:40] + "..." if len(user_message) > 40 else user_message
        await conversation_repo.update_conversation_title(db, conversation_id, title)

    await db.commit()

    # Placeholder: yield a stub response until the engine layer is built
    # The engine layer will plug in here with retriever → augmentor → generator
    stub_response = (
        f"Thank you for your legal question. You asked: \"{user_message}\"\n\n"
        f"This response is a placeholder — the AI engine layer is not yet connected. "
        f"Once the engine is built, this endpoint will:\n"
        f"1. Retrieve relevant legal document chunks from ChromaDB\n"
        f"2. Augment the prompt with context and conversation history\n"
        f"3. Stream the response from the **{model}** model\n"
        f"4. Return source citations\n\n"
        f"*Model selected: {model}*"
    )

    for word in stub_response.split(" "):
        yield json.dumps({"type": "token", "data": word + " "})

    citations = [
        {"document_name": "placeholder.pdf", "page_number": 1, "chunk_text": "Engine not connected yet"}
    ]
    yield json.dumps({"type": "citations", "data": json.dumps(citations)})
    yield json.dumps({"type": "done", "data": ""})

    await message_repo.create_message(db, conversation_id, "assistant", stub_response, citations)
    await db.commit()

    logger.info("Chat response completed conv=%s model=%s", conversation_id, model)
