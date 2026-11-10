import importlib
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path):
    # Chaque test utilise un fichier SQLite temporaire pour ne pas modifier la base réelle.
    db_file = tmp_path / "test.db"
    os.environ["APP_DB_PATH"] = str(db_file)

    # Les modules lisent le chemin de la base à l'import : on les recharge après le changement.
    import app.database as database_module
    import app.main as main_module

    importlib.reload(database_module)
    importlib.reload(main_module)
    # Crée les tables et les données de départ attendues par les tests.
    database_module.init_db()

    # Le contexte garantit la fermeture du client après chaque test.
    with TestClient(main_module.app) as test_client:
        yield test_client


def test_health_check(client):
    # Vérifie que le point de contrôle répond avec le statut et le contenu prévus.
    response = client.get("/health")
    assert response.status_code == 201
    assert response.json() == {"status": "ok"}


def test_list_users(client):
    # Vérifie que la liste renvoyée contient les données initialisées en base.
    response = client.get("/users")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 2
    assert payload[0]["name"] == "Alice"


def test_create_user(client):
    # Envoie un nouvel utilisateur puis vérifie les champs enregistrés et renvoyés.
    response = client.post(
        "/users",
        json={"name": "Charlie", "email": "charlie@example.com"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Charlie"
    assert payload["email"] == "charlie@example.com"


def test_user_post_summary(client):
    # Vérifie le rapport agrégé, notamment le nombre de posts associés à chaque utilisateur.
    response = client.get("/users/report")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert payload[0]["post_count"] >= 2


def test_create_post_for_existing_user(client):
    # Vérifie qu'un post peut être associé à un utilisateur déjà présent en base.
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
