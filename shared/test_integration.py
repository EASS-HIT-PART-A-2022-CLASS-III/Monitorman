import re
import mongomock
from fastapi.testclient import TestClient
import pytest
import requests
from backend.main import app as backend_app
from scheduler.main import app as scheduler_app
import requests_mock
from requests_mock.request import _RequestObjectProxy
from requests_mock.response import _Context
from shared.models import MonitorModel

from shared.mongo import MONGO_DB_NAME, get_prod_client

mongo_test_client = mongomock.MongoClient()


def get_mongo_test_client():
    return mongo_test_client


@pytest.fixture(autouse=True)
def run_around_tests():
    backend_app.dependency_overrides[get_prod_client] = get_mongo_test_client
    scheduler_app.dependency_overrides[get_prod_client] = get_mongo_test_client
    # clean db before every test
    mongo_test_client.drop_database(MONGO_DB_NAME)
    yield


@pytest.fixture()
def example_monitor_dict():
    monitor = MonitorModel(
        description="this is a test monitor",
        url="http://httpbin.org/post",
        method="POST",
        body="{\"hello\":\"world\"}",
        expected_status=200
    ).dict()

    for field in ['id', 'results']+[field for field in monitor if monitor[field] is None]:
        monitor.pop(field)

    return monitor


def test_create_two_and_schedule_all(monkeypatch, example_monitor_dict):
    backend_client = TestClient(backend_app, 'http://localhost:8000')
    scheduler_client = TestClient(scheduler_app, 'http://localhost:8001')

    monkeypatch.setattr(requests, 'request', mock_request)

    with requests_mock.Mocker(real_http=True) as m:
        m: requests_mock.Mocker
        m.get(re.compile('/scheduler/*'),
              json=proxy_scheduler_client(scheduler_client))
        response = backend_client.post('/monitors', json=example_monitor_dict)

        assert response.status_code == 201

        response = backend_client.post('/monitors', json=example_monitor_dict)

        assert response.status_code == 201

    response = scheduler_client.get('/scheduler')

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_create_and_delete_monitor(monkeypatch, example_monitor_dict):
    backend_client = TestClient(backend_app, 'http://localhost:8000')
    scheduler_client = TestClient(scheduler_app, 'http://localhost:8001')

    monkeypatch.setattr(requests, 'request', mock_request)

    with requests_mock.Mocker(real_http=True) as m:
        m: requests_mock.Mocker
        m.get(re.compile('/scheduler/*'),
              json=proxy_scheduler_client(scheduler_client))
        response = backend_client.post('/monitors', json=example_monitor_dict)

    assert response.status_code == 201

    result = response.json()

    assert len(result['results']) == 1

    response = backend_client.delete(f'/monitors/{result["_id"]}')

    assert response.status_code == 204


def mock_request(*args, **kwargs):
    res = requests.Response()
    res.status_code = 200

    return res


def proxy_scheduler_client(client: TestClient):
    def proxy(request: _RequestObjectProxy, context: _Context):
        resp = client.get(request.path)

        return resp.json()
    return proxy
