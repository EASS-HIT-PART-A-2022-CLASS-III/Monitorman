from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest
from ..main import app


@pytest.mark.asyncio
async def test_id_not_found():
    nonexistent_id = '12345678'
    async with AsyncClient(app=app, base_url="http://127.0.0.1") as ac:
        response = await ac.get(f'/scheduler/{nonexistent_id}')

    assert response.status_code == 404
    assert response.json()['detail'] == f"Monitor {nonexistent_id} not found"


@pytest.mark.asyncio
async def test_trigger_all():
    async with AsyncClient(app=app, base_url="http://127.0.0.1") as ac:
        response = await ac.get('/scheduler/')

    assert response.status_code == 200
    assert response.json() == []
