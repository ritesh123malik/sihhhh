import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

VALID_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
VALID_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


class TestSuccessfulPrediction:
    def test_jpeg(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/predict",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            pred = body["prediction"]
            assert pred["label"] in ("MOCK_CLASS_A", "MOCK_CLASS_B", "MOCK_CLASS_C")
            assert 0.0 <= pred["confidence"] <= 1.0
            assert isinstance(pred["raw_scores"], dict)
            assert len(pred["raw_scores"]) == 3
            model = body["model"]
            assert model["name"] == "sonar-model"
            assert model["version"] == "development"
            assert model["provider"] == "mock"
            uuid.UUID(body["request_id"])

    def test_png(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/predict",
                files={"file": ("test.png", VALID_PNG, "image/png")},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert body["prediction"]["label"] in (
                "MOCK_CLASS_A",
                "MOCK_CLASS_B",
                "MOCK_CLASS_C",
            )
            uuid.UUID(body["request_id"])


class TestDeterminism:
    def test_same_input_same_prediction(self):
        with TestClient(app) as c:
            r1 = c.post(
                "/api/predict",
                files={"file": ("a.jpg", VALID_JPEG, "image/jpeg")},
            )
            r2 = c.post(
                "/api/predict",
                files={"file": ("b.jpg", VALID_JPEG, "image/jpeg")},
            )
            assert r1.json()["prediction"] == r2.json()["prediction"]

    def test_different_inputs_can_differ(self):
        """Different inputs may produce different labels, but the mock
        has a finite label space so we only verify the pipeline runs."""
        with TestClient(app) as c:
            r1 = c.post(
                "/api/predict",
                files={"file": ("a.jpg", VALID_JPEG, "image/jpeg")},
            )
            r2 = c.post(
                "/api/predict",
                files={"file": ("b.png", VALID_PNG, "image/png")},
            )
            assert r1.status_code == 200
            assert r2.status_code == 200


class TestMissingFile:
    def test_no_file(self):
        with TestClient(app) as c:
            resp = c.post("/api/predict")
            assert resp.status_code == 400
            body = resp.json()
            assert body["success"] is False
            assert body["error"]["code"] == "NO_FILE"


class TestInvalidFileType:
    def test_wrong_mime(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/predict",
                files={"file": ("test.txt", b"hello", "text/plain")},
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"

    def test_jpeg_magic_mismatch(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/predict",
                files={"file": ("test.jpg", b"not_jpeg", "image/jpeg")},
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"

    def test_png_magic_mismatch(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/predict",
                files={"file": ("test.png", b"not_png", "image/png")},
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"


class TestFileTooLarge:
    def test_oversized_file(self):
        from app.config import Settings

        tiny = Settings(
            model_provider="mock",
            max_file_size_mb=0,
        )
        with TestClient(app) as c:
            with patch("app.api.routes.predict.get_settings", return_value=tiny):
                big_content = b"\xff\xd8\xff\xe0" + b"\x00" * 2000
                resp = c.post(
                    "/api/predict",
                    files={"file": ("big.jpg", big_content, "image/jpeg")},
                )
                assert resp.status_code == 400
                assert resp.json()["error"]["code"] == "FILE_TOO_LARGE"


class TestInferenceFailure:
    def test_returns_500(self):
        with TestClient(app) as c:
            with patch.object(
                type(app.state.inference_service),
                "predict",
                side_effect=RuntimeError("boom"),
            ):
                resp = c.post(
                    "/api/predict",
                    files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                )
                assert resp.status_code == 500
                body = resp.json()
                assert body["success"] is False
                assert body["error"]["code"] == "INFERENCE_FAILED"
                assert "boom" not in body["error"]["message"]


class TestHealthUnchanged:
    def test_health_still_works(self):
        with TestClient(app) as c:
            resp = c.get("/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
            assert resp.json()["model"]["loaded"] is True
