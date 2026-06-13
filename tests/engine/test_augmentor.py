from engine.orchestration.augmentor import augment
from engine.prompts.templates import SYSTEM_PROMPT


def test_augment_basic():
    chunks = [
        {
            "content": "Tort law covers civil wrongs.",
            "metadata": {"filename": "torts.pdf", "page_number": 1},
            "distance": 0.2,
        }
    ]
    messages = augment("What is tort law?", chunks)
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert messages[1]["role"] == "user"
    assert "What is tort law?" in messages[1]["content"]
    assert "torts.pdf" in messages[1]["content"]


def test_augment_with_history():
    chunks = [
        {
            "content": "Contract law basics.",
            "metadata": {"filename": "contracts.pdf", "page_number": 5},
            "distance": 0.3,
        }
    ]
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello! How can I help?"},
    ]
    messages = augment("Explain contracts", chunks, history)
    assert len(messages) == 4
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "Hi"
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "user"
    assert "Explain contracts" in messages[3]["content"]


def test_augment_no_chunks():
    messages = augment("Random question", [])
    assert len(messages) == 2
    assert "No relevant documents found" in messages[1]["content"]


def test_augment_no_history():
    chunks = [
        {
            "content": "Some text",
            "metadata": {"filename": "doc.pdf", "page_number": 1},
            "distance": 0.1,
        }
    ]
    messages = augment("Question?", chunks, None)
    assert len(messages) == 2


def test_augment_multiple_chunks():
    chunks = [
        {"content": "Chunk one.", "metadata": {"filename": "a.pdf", "page_number": 1}, "distance": 0.1},
        {"content": "Chunk two.", "metadata": {"filename": "b.pdf", "page_number": 3}, "distance": 0.2},
        {"content": "Chunk three.", "metadata": {"filename": "a.pdf", "page_number": 7}, "distance": 0.3},
    ]
    messages = augment("Complex query", chunks)
    user_msg = messages[1]["content"]
    assert "Source 1" in user_msg
    assert "Source 2" in user_msg
    assert "Source 3" in user_msg
