import json
import logging
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.data.repositories import conversation_repo, message_repo
from server.app.exceptions import ConversationNotFoundError

from engine.orchestration.retriever import retrieve
from engine.orchestration.augmentor import augment
from engine.orchestration.generator import generate_stream

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

    try:
        logger.info("Retrieving relevant chunks for query")
        retrieved_chunks = retrieve(user_message)
        logger.info("Retrieved %d chunk(s)", len(retrieved_chunks))

        history = []
        messages = await message_repo.get_messages_by_conversation(db, conversation_id)
        for msg in messages:
            if msg.role in ("user", "assistant") and msg.content:
                history.append({"role": msg.role, "content": msg.content})
        # Exclude the last user message since it's already the current query
        if history and history[-1]["role"] == "user":
            history = history[:-1]

        logger.info("Building augmented prompt with %d history message(s)", len(history))
        augmented_messages = augment(user_message, retrieved_chunks, history if history else None)

        logger.info("Streaming LLM response with model=%s", model)
        full_response = ""
        for token in generate_stream(augmented_messages, model):
            full_response += token
            yield json.dumps({"type": "token", "data": token})

        citations = []
        for chunk in retrieved_chunks:
            citations.append({
                "document_name": chunk["metadata"].get("filename", "unknown"),
                "page_number": chunk["metadata"].get("page_number", 0),
                "chunk_text": chunk["content"][:200],
            })

        yield json.dumps({"type": "citations", "data": json.dumps(citations)})
        yield json.dumps({"type": "done", "data": ""})

        await message_repo.create_message(
            db, conversation_id, "assistant", full_response, citations
        )
        await db.commit()

        logger.info("Chat response completed conv=%s model=%s chars=%d", conversation_id, model, len(full_response))

    except Exception as e:
        logger.error("Chat processing failed: %s", str(e))
        error_msg = f"An error occurred while processing your question: {str(e)}"
        yield json.dumps({"type": "token", "data": error_msg})
        yield json.dumps({"type": "done", "data": ""})

        await message_repo.create_message(db, conversation_id, "assistant", error_msg, [])
        await db.commit()
