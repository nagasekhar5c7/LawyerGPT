"""
Augmentor (second step of Query Orchestration pipeline).

Takes the user query, retrieved context chunks, and optional conversation
history, then assembles them into a structured messages list ready to be
sent to the LLM in generator.py.

Output format: list of dicts with "role" and "content" keys, compatible
with OpenAI/Anthropic chat completion APIs.
"""

import logging
from engine.prompts.templates import SYSTEM_PROMPT, CONTEXT_TEMPLATE, format_context

logger = logging.getLogger("lawyergpt.engine.augmentor")


def augment(
    user_query: str,
    retrieved_chunks: list[dict],
    conversation_history: list[dict] | None = None,
) -> list[dict]:
    """
    Build the augmented prompt (messages list) for the LLM.

    Args:
        user_query: The user's current question
        retrieved_chunks: List of dicts from retriever, each with
            content, metadata, and distance
        conversation_history: Optional list of prior messages, each with
            "role" and "content" keys

    Returns:
        List of message dicts with "role" and "content", ready for the LLM:
          [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},      # history
            {"role": "assistant", "content": "..."},  # history
            {"role": "user", "content": "..."},       # current query + context
          ]
    """
    logger.info(
        "Augmenting query (%d chars) with %d retrieved chunk(s) and %d history message(s)",
        len(user_query),
        len(retrieved_chunks),
        len(conversation_history) if conversation_history else 0,
    )

    messages: list[dict] = []

    messages.append({"role": "system", "content": SYSTEM_PROMPT})

    if conversation_history:
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })

    context_str = format_context(retrieved_chunks)
    context_block = CONTEXT_TEMPLATE.format(context=context_str)

    user_message = f"{context_block}\n\nUSER QUESTION:\n{user_query}"
    messages.append({"role": "user", "content": user_message})

    logger.info(
        "Augmented prompt: %d message(s), total chars=%d",
        len(messages),
        sum(len(m["content"]) for m in messages),
    )
    return messages


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    from engine.orchestration.retriever import retrieve

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is tort law?"

    retrieved = retrieve(query)
    messages = augment(query, retrieved)

    print(f"\n{'='*60}")
    print(f"AUGMENTOR RESULTS")
    print(f"{'='*60}")
    print(f"Query:            \"{query}\"")
    print(f"Retrieved chunks: {len(retrieved)}")
    print(f"Messages built:   {len(messages)}")
    print(f"Total chars:      {sum(len(m['content']) for m in messages)}")
    print(f"{'='*60}\n")

    for i, msg in enumerate(messages):
        role = msg["role"].upper()
        content = msg["content"]
        print(f"--- Message {i + 1} [{role}] ({len(content)} chars) ---")
        if len(content) > 500:
            print(content[:500])
            print(f"  ... ({len(content) - 500} more chars)")
        else:
            print(content)
        print()
