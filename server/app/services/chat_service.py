import json
import logging
import re
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.data.repositories import conversation_repo, message_repo
from server.app.exceptions import ConversationNotFoundError

from engine.orchestration.retriever import retrieve
from engine.orchestration.augmentor import augment
from engine.orchestration.generator import generate_stream

logger = logging.getLogger("lawyergpt.service.chat")

GREETING_PATTERNS = re.compile(
    r"^\s*(hi|hello|hey|howdy|greetings|good\s*(morning|afternoon|evening|night)|"
    r"bye|goodbye|see\s*you|farewell|thanks|thank\s*you|how\s*are\s*you|"
    r"what'?s\s*up|sup|yo)\s*[!?.]*\s*$",
    re.IGNORECASE,
)

INSUFFICIENT_INFO_PATTERNS = re.compile(
    r"(do(es)?\s*not\s*contain\s*sufficient\s*information|"
    r"insufficient\s*information|"
    r"cannot\s*(be\s*)?answer(ed)?|"
    r"not\s*(enough|sufficient)\s*(information|context|data)|"
    r"no\s*relevant\s*(information|context|documents?)|"
    r"does\s*not\s*(address|discuss|cover|mention)|"
    r"outside\s*the\s*scope|"
    r"not\s*related\s*to)",
    re.IGNORECASE,
)

RELEVANCE_DISTANCE_THRESHOLD = 1.0


def _is_greeting(text: str) -> bool:
    return bool(GREETING_PATTERNS.match(text.strip()))


def _should_include_citations(response_text: str, retrieved_chunks: list[dict]) -> list[dict]:
    if INSUFFICIENT_INFO_PATTERNS.search(response_text):
        logger.info("Suppressing citations — LLM indicated insufficient information")
        return []

    relevant = [c for c in retrieved_chunks if c.get("distance", 999) < RELEVANCE_DISTANCE_THRESHOLD]
    if not relevant:
        logger.info("Suppressing citations — no chunks below distance threshold %.2f", RELEVANCE_DISTANCE_THRESHOLD)
        return []

    return relevant


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
        if _is_greeting(user_message):
            logger.info("Query classified as greeting — skipping retrieval")
            retrieved_chunks = []
            augmented_messages = augment(user_message, [], None)
        else:
            logger.info("Retrieving relevant chunks for query")
            retrieved_chunks = retrieve(user_message)
            logger.info("Retrieved %d chunk(s)", len(retrieved_chunks))

        history = []
        messages = await message_repo.get_messages_by_conversation(db, conversation_id)
        for msg in messages:
            if msg.role in ("user", "assistant") and msg.content:
                history.append({"role": msg.role, "content": msg.content})
        if history and history[-1]["role"] == "user":
            history = history[:-1]

        if not _is_greeting(user_message):
            logger.info("Building augmented prompt with %d history message(s)", len(history))
            augmented_messages = augment(user_message, retrieved_chunks, history if history else None)

        logger.info("Streaming LLM response with model=%s", model)
        full_response = ""
        for token in generate_stream(augmented_messages, model):
            full_response += token
            yield json.dumps({"type": "token", "data": token})

        if _is_greeting(user_message):
            citations = []
            logger.info("Greeting — no citations to send")
        else:
            relevant_chunks = _should_include_citations(full_response, retrieved_chunks)
            citations = []
            for chunk in relevant_chunks:
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

        logger.info("Chat response completed conv=%s model=%s chars=%d citations=%d", conversation_id, model, len(full_response), len(citations))

    except Exception as e:
        logger.error("Chat processing failed: %s", str(e))
        error_msg = f"An error occurred while processing your question: {str(e)}"
        yield json.dumps({"type": "token", "data": error_msg})
        yield json.dumps({"type": "done", "data": ""})

        await message_repo.create_message(db, conversation_id, "assistant", error_msg, [])
        await db.commit()
