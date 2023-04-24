import mongomock
from fastapi.testclient import TestClient
import pytest

from shared.mongo import MONGO_DB_NAME, MONITORS_COLLECTION_NAME, get_prod_client

from ..main import app

mongo_test_client = mongomock.MongoClient()


def get_mongo_test_client():
    return mongo_test_client


@pytest.fixture(autouse=True)
def run_around_tests():
    app.dependency_overrides[get_prod_client] = get_mongo_test_client
    # clean db before every test
    mongo_test_client.drop_database(MONGO_DB_NAME)
    yield


def test_id_not_found():
    nonexistent_id = '12345678'
    client = TestClient(app)
    response = client.get(f'/scheduler/{nonexistent_id}')

    assert response.status_code == 404
    assert response.json()['detail'] == f"Monitor {nonexistent_id} not found"


def test_monitor_success():
    db = mongo_test_client[MONGO_DB_NAME]
    collection = db[MONITORS_COLLECTION_NAME]
    monitor_id = "666f6f2d6261722d71757578"
    collection.insert_one(
        {"url": "http://httpbin.org/get", "method": "GET", "_id": monitor_id})

    client = TestClient(app)
    response = client.get(f'/scheduler/{monitor_id}')

    assert response.status_code == 200


def test_trigger_all_empty():
    client = TestClient(app)
    response = client.get('/scheduler/')

    assert response.status_code == 200
    assert response.json() == []
