import uuid

from fastapi.testclient import TestClient

from app.main import app

VALID_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
VALID_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        with TestClient(app) as c:
            resp = c.get("/api/health")
            assert resp.status_code == 200
            body = resp.json()
            assert body["status"] == "ok"
            assert "model" in body
            assert body["model"]["loaded"] is True
            assert body["model"]["provider"] == "mock"

    def test_health_database_status(self):
        with TestClient(app) as c:
            resp = c.get("/api/health")
            assert resp.status_code == 200
            body = resp.json()
            assert body["database"]["status"] == "ok"

    def test_legacy_health_still_works(self):
        with TestClient(app) as c:
            resp = c.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
