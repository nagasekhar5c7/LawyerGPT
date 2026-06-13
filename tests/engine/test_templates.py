from engine.prompts.templates import SYSTEM_PROMPT, CONTEXT_TEMPLATE, format_context


def test_system_prompt_contains_key_instructions():
    assert "LawyerGPT" in SYSTEM_PROMPT
    assert "cite" in SYSTEM_PROMPT.lower()
    assert "fabricate" in SYSTEM_PROMPT.lower()
    assert "legal" in SYSTEM_PROMPT.lower()


def test_context_template_has_placeholder():
    assert "{context}" in CONTEXT_TEMPLATE


def test_format_context_empty():
    result = format_context([])
    assert result == "No relevant documents found."


def test_format_context_single_chunk():
    chunks = [
        {
            "content": "The defendant is liable.",
            "metadata": {"filename": "case.pdf", "page_number": 12},
        }
    ]
    result = format_context(chunks)
    assert "Source 1" in result
    assert "case.pdf" in result
    assert "Page 12" in result
    assert "The defendant is liable." in result


def test_format_context_multiple_chunks():
    chunks = [
        {"content": "First.", "metadata": {"filename": "a.pdf", "page_number": 1}},
        {"content": "Second.", "metadata": {"filename": "b.pdf", "page_number": 2}},
    ]
    result = format_context(chunks)
    assert "Source 1" in result
    assert "Source 2" in result
    assert "a.pdf" in result
    assert "b.pdf" in result
