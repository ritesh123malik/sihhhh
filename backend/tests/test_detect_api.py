import uuid

from fastapi.testclient import TestClient

from app.main import app

VALID_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100
VALID_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


class TestDetectSuccess:
    def test_jpeg_detect(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert body["status"] == "completed"
            assert body["run_id"]
            assert body["mission_id"].startswith("MSN-")
            assert body["scan_metadata"]["filename"] == "test.jpg"
            assert body["scan_metadata"]["latitude"] == 12.9716
            assert body["scan_metadata"]["longitude"] == 80.2436
            assert body["scan_metadata"]["sonar_type"] == "Side-Scan"
            assert body["scan_metadata"]["resolution"] == "0.5 m/px"
            assert body["scan_metadata"]["depth_min"] == 4.0
            assert body["scan_metadata"]["depth_max"] == 38.0
            assert body["detection_summary"]["total"] > 0
            assert len(body["detections"]) > 0
            assert body["model"]["provider"] == "mock"
            assert body["timestamps"]["duration_seconds"] >= 0

    def test_png_detect(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.png", VALID_PNG, "image/png")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Multibeam",
                    "resolution": "0.1 m/px",
                    "depth_min": "0",
                    "depth_max": "50",
                },
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert body["scan_metadata"]["sonar_type"] == "Multibeam"

    def test_detection_structure(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            body = resp.json()
            det = body["detections"][0]
            assert "detection_id" in det
            assert "class_label" in det
            assert "confidence" in det
            assert "risk_level" in det
            assert 0.0 <= det["confidence"] <= 1.0
            assert det["risk_level"] in ("low", "medium", "high", "critical")


class TestDetectMissingFile:
    def test_no_file(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "NO_FILE"


class TestDetectInvalidFileType:
    def test_wrong_mime(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.txt", b"hello", "text/plain")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"

    def test_magic_bytes_mismatch(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.jpg", b"not_jpeg", "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_FILE_TYPE"


class TestDetectInvalidMetadata:
    def test_depth_min_greater_than_depth_max(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "38",
                    "depth_max": "4",
                },
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_METADATA"

    def test_invalid_sonar_type(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "InvalidType",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_METADATA"

    def test_invalid_resolution(self):
        with TestClient(app) as c:
            resp = c.post(
                "/api/detect",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "100 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            assert resp.status_code == 400
            assert resp.json()["error"]["code"] == "INVALID_METADATA"


class TestDetectDeterminism:
    def test_same_input_same_result(self):
        with TestClient(app) as c:
            r1 = c.post(
                "/api/detect",
                files={"file": ("a.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            r2 = c.post(
                "/api/detect",
                files={"file": ("b.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                },
            )
            assert r1.json()["detection_summary"] == r2.json()["detection_summary"]


class TestDetectThreshold:
    def test_high_threshold_hides_lower_confidence(self):
        with TestClient(app) as c:
            baseline = c.post(
                "/api/detect",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                    "confidence_threshold": "15",
                },
            ).json()
            filtered = c.post(
                "/api/detect",
                files={"file": ("test.jpg", VALID_JPEG, "image/jpeg")},
                data={
                    "latitude": "12.9716",
                    "longitude": "80.2436",
                    "sonar_type": "Side-Scan",
                    "resolution": "0.5 m/px",
                    "depth_min": "4",
                    "depth_max": "38",
                    "confidence_threshold": "80",
                },
            ).json()
            for det in filtered["detections"]:
                assert round(det["confidence"] * 100) >= 80
            assert filtered["detection_summary"]["total"] <= baseline["detection_summary"]["total"]
