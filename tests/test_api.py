import importlib
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    db_file = tmp_path / "test.db"
    os.environ["APP_DB_PATH"] = str(db_file)

    import app.database as database_module
    import app.main as main_module

    importlib.reload(database_module)
    importlib.reload(main_module)
    database_module.init_db()

    with TestClient(main_module.app) as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 2
    assert payload[0]["name"] == "Alice"


def test_create_user(client):
    response = client.post(
        "/users",
        json={"name": "Charlie", "email": "charlie@example.com"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Charlie"
    assert payload["email"] == "charlie@example.com"


def test_user_post_summary(client):
    response = client.get("/users/report")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["post_count"] >= 2


def test_create_post_for_existing_user(client):
    response = client.post(
        "/posts",
        json={
            "title": "SQL practice",
            "body": "Testing database queries",
            "user_id": 1,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "SQL practice"
    assert payload["user_id"] == 1
