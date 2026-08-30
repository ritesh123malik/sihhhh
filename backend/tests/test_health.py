import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
VALID_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def test_app_imports():
    assert app is not None


def test_health_returns_model_loaded_true():
    with TestClient(app) as c:
        response = c.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["model"]["loaded"] is True
        assert body["database"]["status"] == "ok"


def test_docs_loads():
    with TestClient(app) as c:
        response = c.get("/docs")
        assert response.status_code == 200
