import datetime
import json
import re

import mongomock
import pytest
from fastapi.testclient import TestClient

from backend.models import UpdateMonitorModel
from shared.models import CheckModel, MonitorModel, ResultModel
from shared.mongo import (MONGO_DB_NAME, MONITORS_COLLECTION_NAME,
                          get_prod_client)

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


@pytest.fixture()
def example_monitor_id():
    return "666f6f2d6261722d71757578"


@pytest.fixture()
def example_monitor(example_monitor_id):
    monitor = MonitorModel(
        description="this is a test monitor",
        url="http://httpbin.org/post",
        method="POST",
        body="{\"hello\":\"world\"}",
        checks=CheckModel(expected_status=200),
        results=[ResultModel(status=200, time=datetime.datetime.now(), content='wow',
                             duration_ms=5000, headers={}, checked_with=CheckModel(expected_status=200))]
    ).dict()

    monitor['_id'] = example_monitor_id

    return monitor


@pytest.fixture()
def example_update_monitor():
    return UpdateMonitorModel(
        description="updated_description",
        url="http://httpbin.org/get",
        method="GET",
        body="",
        checks=CheckModel(expected_status=404)
    ).dict()


def test_now_allowed():
    client = TestClient(app)
    response = client.post('/monitors/v1/getmonitors/false')

    assert response.status_code == 405


@pytest.mark.parametrize("with_results,results_len", [(False, 0), (True, 1)])
def test_with_results(example_monitor, with_results, results_len):
    db = mongo_test_client[MONGO_DB_NAME]
    collection = db[MONITORS_COLLECTION_NAME]
    collection.insert_one(example_monitor)

    client = TestClient(app)
    response = client.get(f'/monitors/v1/getmonitors/{with_results}')
    result = response.json()

    assert response.status_code == 200
    assert len(result) == 1
    assert len(result[0]['results']) == results_len


def test_update_nonexistent(example_update_monitor):
    nonexistent_id = '12345678'

    client = TestClient(app)
    response = client.put(
        f'/monitors/v1/{nonexistent_id}', json=example_update_monitor)

    assert response.status_code == 404
    assert response.json()['detail'] == f"Monitor {nonexistent_id} not found"


def test_update(example_monitor, example_monitor_id, example_update_monitor):
    db = mongo_test_client[MONGO_DB_NAME]
    collection = db[MONITORS_COLLECTION_NAME]
    collection.insert_one(example_monitor)

    client = TestClient(app)

    response = client.put(
        f'/monitors/v1/{example_monitor_id}', json=example_update_monitor)

    assert response.status_code == 200

    result = response.json()

    for field in example_update_monitor:
        assert result[field] == (
            example_monitor[field] if example_update_monitor[field] is None else example_update_monitor[field])


def test_id_not_found(example_monitor_id):
    client = TestClient(app)
    response = client.get(f'/monitors/v1/{example_monitor_id}')

    assert response.status_code == 404
    assert response.json()[
        'detail'] == f"Monitor {example_monitor_id} not found"


def test_get_monitors_empty():
    client = TestClient(app)
    response = client.get('/monitors/v1/getmonitors/false')

    assert response.status_code == 200
    assert response.json() == []


def test_create_monitor(example_monitor):
    del example_monitor['id']
    del example_monitor['results']

    client = TestClient(app)
    response = client.post(
        f'/monitors/v1', json=json.loads(json.dumps(example_monitor, default=str)))

    assert response.status_code == 201

    result = response.json()

    for field in example_monitor:
        assert result[field] == example_monitor[field]


def test_get_monitor(example_monitor, example_monitor_id):
    db = mongo_test_client[MONGO_DB_NAME]
    collection = db[MONITORS_COLLECTION_NAME]
    collection.insert_one(example_monitor)

    client = TestClient(app)

    response = client.get(f'/monitors/v1/{example_monitor_id}')

    assert response.status_code == 200
    assert response.json()['_id'] == example_monitor_id


def test_delete_monitor(example_monitor, example_monitor_id):
    db = mongo_test_client[MONGO_DB_NAME]
    collection = db[MONITORS_COLLECTION_NAME]
    collection.insert_one(example_monitor)

    client = TestClient(app)

    response = client.delete(f'/monitors/v1/{example_monitor_id}')

    assert response.status_code == 204
