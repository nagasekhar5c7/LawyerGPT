from datetime import datetime, timezone
from server.app.schemas.chat import ChatRequest
from server.app.schemas.conversation import (
    MessageResponse,
    ConversationResponse,
    ConversationWithMessagesResponse,
)
from server.app.schemas.document import DocumentResponse


def test_chat_request_defaults():
    req = ChatRequest(message="What is tort law?")
    assert req.message == "What is tort law?"
    assert req.model == "gpt-5.5"


def test_chat_request_custom_model():
    req = ChatRequest(message="Hello", model="claude-sonnet-4-6")
    assert req.model == "claude-sonnet-4-6"


def test_message_response():
    msg = MessageResponse(
        id="abc-123",
        conversation_id="conv-456",
        role="assistant",
        content="Legal answer here",
        citations=[],
        created_at=datetime.now(timezone.utc),
    )
    assert msg.role == "assistant"
    assert msg.citations == []


def test_conversation_response():
    now = datetime.now(timezone.utc)
    conv = ConversationResponse(
        id="conv-1", title="New Chat", created_at=now, updated_at=now
    )
    assert conv.title == "New Chat"


def test_conversation_with_messages_response():
    now = datetime.now(timezone.utc)
    conv = ConversationWithMessagesResponse(
        id="conv-1", title="Test", created_at=now, updated_at=now, messages=[]
    )
    assert conv.messages == []


def test_document_response():
    doc = DocumentResponse(
        id="doc-1",
        filename="contract.pdf",
        file_size=1024,
        total_chunks=10,
        status="completed",
        created_at=datetime.now(timezone.utc),
    )
    assert doc.filename == "contract.pdf"
    assert doc.status == "completed"
