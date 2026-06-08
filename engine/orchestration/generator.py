"""
Generator (third step of Query Orchestration pipeline).

Takes the augmented messages list from augmentor.py and sends it to the
selected LLM. Supports both OpenAI and Anthropic models. Returns the
full response text and supports streaming via a callback.
"""

import logging
import os
from collections.abc import Generator
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

load_dotenv()

logger = logging.getLogger("lawyergpt.engine.generator")

DEFAULT_MODEL = os.getenv("DEFAULT_LLM_MODEL", "gpt-5.5")

OPENAI_MODELS = {"gpt-5.5", "gpt-4o", "gpt-4o-mini"}
ANTHROPIC_MODELS = {"claude-sonnet-4-6", "claude-haiku-4-5"}


def _build_langchain_messages(messages: list[dict]) -> list:
    """Convert plain dicts to LangChain message objects."""
    lc_messages = []
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            lc_messages.append(SystemMessage(content=content))
        elif role == "user":
            lc_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            lc_messages.append(AIMessage(content=content))
    return lc_messages


def _get_llm(model: str):
    """Instantiate the correct LLM based on model ID."""
    if model in OPENAI_MODELS:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAI models")
        return ChatOpenAI(model=model, openai_api_key=api_key, temperature=0.2)

    if model in ANTHROPIC_MODELS:
        api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for Anthropic models")
        return ChatAnthropic(model=model, anthropic_api_key=api_key, temperature=0.2)

    raise ValueError(f"Unsupported model: {model}. Supported: {OPENAI_MODELS | ANTHROPIC_MODELS}")


def generate(messages: list[dict], model: str = DEFAULT_MODEL) -> str:
    """
    Send augmented messages to the LLM and return the full response.

    Args:
        messages: List of dicts with "role" and "content" from augmentor
        model: Model ID to use (e.g. "gpt-5.5", "claude-sonnet-4-6")

    Returns:
        The complete LLM response as a string
    """
    logger.info("Generating response with model=%s (%d messages)", model, len(messages))

    llm = _get_llm(model)
    lc_messages = _build_langchain_messages(messages)

    response = llm.invoke(lc_messages)

    logger.info("Generation complete (%d chars)", len(response.content))
    return response.content


def generate_stream(messages: list[dict], model: str = DEFAULT_MODEL) -> Generator[str, None, None]:
    """
    Send augmented messages to the LLM and stream the response token by token.

    Args:
        messages: List of dicts with "role" and "content" from augmentor
        model: Model ID to use

    Yields:
        Token strings as they arrive from the LLM
    """
    logger.info("Streaming response with model=%s (%d messages)", model, len(messages))

    llm = _get_llm(model)
    lc_messages = _build_langchain_messages(messages)

    full_response = ""
    for chunk in llm.stream(lc_messages):
        token = chunk.content
        if token:
            full_response += token
            yield token

    logger.info("Stream complete (%d chars)", len(full_response))


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    from engine.orchestration.retriever import retrieve
    from engine.orchestration.augmentor import augment

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is tort law?"
    model = os.getenv("LLM_MODEL", DEFAULT_MODEL)

    retrieved = retrieve(query)
    messages = augment(query, retrieved)

    print(f"\n{'='*60}")
    print(f"GENERATOR")
    print(f"{'='*60}")
    print(f"Query: \"{query}\"")
    print(f"Model: {model}")
    print(f"Retrieved chunks: {len(retrieved)}")
    print(f"Messages: {len(messages)}")
    print(f"{'='*60}\n")

    print("--- Streaming Response ---\n")
    full = ""
    for token in generate_stream(messages, model):
        print(token, end="", flush=True)
        full += token

    print(f"\n\n{'='*60}")
    print(f"Response length: {len(full)} chars")
    print(f"{'='*60}")
