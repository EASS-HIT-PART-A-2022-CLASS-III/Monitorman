import re
import mongomock
from fastapi.testclient import TestClient
import pytest

from shared.mongo import MONGO_DB_NAME, MONITORS_COLLECTION_NAME, get_prod_client

from ..main import app

mongo_test_client = mongomock.MongoClient()


def get_mongo_test_client():
    return mongo_test_client




@pytest.fixture(autouse=True)
def run_around_tests(requests_mock):
    app.dependency_overrides[get_prod_client] = get_mongo_test_client
    requests_mock.get(re.compile('/scheduler/*'))
    # clean db before every test
    mongo_test_client.drop_database(MONGO_DB_NAME)
    yield


def test_id_not_found():
    nonexistent_id = '12345678'
    client = TestClient(app)
    response = client.get(f'/monitors/{nonexistent_id}')

    assert response.status_code == 404
    assert response.json()['detail'] == f"Monitor {nonexistent_id} not found"


def test_get_monitors_empty():
    client = TestClient(app)
    response = client.get('/monitors/getmonitors/false')

    assert response.status_code == 200
    assert response.json() == []


def test_create_monitor():
    client = TestClient(app)

    data = {
        "description": "this is a test monitor",
        "url": "http://httpbin.org/post",
        "method": "POST",
        "body": "{\"hello\":\"world\"}",
        "expected_status": 200,
    }

    response = client.post(f'/monitors', json=data)

    assert response.status_code == 201

    result = response.json()

    print(result)

    for field in data:
        assert result[field] == data[field]


def test_get_monitor():
    db = mongo_test_client[MONGO_DB_NAME]
    collection = db[MONITORS_COLLECTION_NAME]
    monitor_id = "666f6f2d6261722d71757578"
    collection.insert_one(
        {"url": "http://httpbin.org/get", "method": "GET", "_id": monitor_id})

    client = TestClient(app)

    response = client.get(f'/monitors/{monitor_id}')

    assert response.status_code == 200
    assert response.json()['_id'] == monitor_id


def test_delete_monitor():
    db = mongo_test_client[MONGO_DB_NAME]
    collection = db[MONITORS_COLLECTION_NAME]
    monitor_id = "666f6f2d6261722d71757578"
    collection.insert_one(
        {"url": "http://httpbin.org/get", "method": "GET", "_id": monitor_id})

    client = TestClient(app)

    response = client.delete(f'/monitors/{monitor_id}')

    assert response.status_code == 204
