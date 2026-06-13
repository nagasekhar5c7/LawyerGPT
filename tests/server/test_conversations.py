import pytest


@pytest.mark.asyncio
async def test_create_conversation(client):
    response = await client.post("/api/v1/conversations")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "New Chat"
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_list_conversations_empty(client):
    response = await client.get("/api/v1/conversations")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_conversations_after_create(client):
    await client.post("/api/v1/conversations")
    await client.post("/api/v1/conversations")

    response = await client.get("/api/v1/conversations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_conversation_by_id(client):
    create_resp = await client.post("/api/v1/conversations")
    conv_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv_id
    assert data["messages"] == []


@pytest.mark.asyncio
async def test_get_conversation_not_found(client):
    response = await client.get("/api/v1/conversations/nonexistent-id")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "CONVERSATION_NOT_FOUND"


@pytest.mark.asyncio
async def test_delete_conversation(client):
    create_resp = await client.post("/api/v1/conversations")
    conv_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/v1/conversations/{conv_id}")
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/v1/conversations/{conv_id}")
    assert get_resp.status_code == 400


@pytest.mark.asyncio
async def test_delete_conversation_not_found(client):
    response = await client.delete("/api/v1/conversations/nonexistent-id")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "CONVERSATION_NOT_FOUND"
