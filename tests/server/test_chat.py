import pytest


@pytest.mark.asyncio
async def test_chat_conversation_not_found(client):
    response = await client.post(
        "/api/v1/chat/nonexistent-id",
        json={"message": "Hello", "model": "gpt-5.5"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "CONVERSATION_NOT_FOUND"
