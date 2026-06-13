import pytest


@pytest.mark.asyncio
async def test_list_documents_empty(client):
    response = await client.get("/api/v1/documents")
    assert response.status_code == 200
    assert response.json() == []
