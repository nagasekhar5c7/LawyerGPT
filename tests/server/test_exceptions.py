from server.app.exceptions import (
    LawyerGPTError,
    ConversationNotFoundError,
    DocumentProcessingError,
    LLMError,
    RetrievalError,
)


def test_lawyergpt_error():
    err = LawyerGPTError("something broke", "CUSTOM_ERROR")
    assert err.message == "something broke"
    assert err.error_code == "CUSTOM_ERROR"
    assert str(err) == "something broke"


def test_lawyergpt_error_defaults():
    err = LawyerGPTError("oops")
    assert err.error_code == "INTERNAL_ERROR"


def test_conversation_not_found():
    err = ConversationNotFoundError("conv-123")
    assert "conv-123" in err.message
    assert err.error_code == "CONVERSATION_NOT_FOUND"


def test_document_processing_error():
    err = DocumentProcessingError("PDF corrupt")
    assert err.message == "PDF corrupt"
    assert err.error_code == "DOCUMENT_PROCESSING_ERROR"


def test_llm_error():
    err = LLMError("rate limited")
    assert err.error_code == "LLM_ERROR"


def test_retrieval_error():
    err = RetrievalError("ChromaDB down")
    assert err.error_code == "RETRIEVAL_ERROR"
