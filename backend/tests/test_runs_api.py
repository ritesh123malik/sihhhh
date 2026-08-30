from fastapi.testclient import TestClient

from app.main import app

VALID_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100


def _create_run(client):
    resp = client.post(
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
    return resp.json()["run_id"]


class TestListRuns:
    def test_empty_runs(self):
        with TestClient(app) as c:
            resp = c.get("/api/runs")
            assert resp.status_code == 200
            body = resp.json()
            assert body["items"] == []
            assert body["pagination"]["total"] == 0

    def test_runs_after_detect(self):
        with TestClient(app) as c:
            run_id = _create_run(c)
            resp = c.get("/api/runs")
            assert resp.status_code == 200
            body = resp.json()
            assert body["pagination"]["total"] == 1
            assert body["items"][0]["run_id"] == run_id
            assert body["items"][0]["latitude"] == 12.9716
            assert body["items"][0]["longitude"] == 80.2436

    def test_runs_pagination(self):
        with TestClient(app) as c:
            for _ in range(5):
                _create_run(c)
            resp = c.get("/api/runs", params={"page": 1, "page_size": 2})
            body = resp.json()
            assert len(body["items"]) == 2
            assert body["pagination"]["total"] == 5
            assert body["pagination"]["total_pages"] == 3

    def test_runs_status_filter(self):
        with TestClient(app) as c:
            _create_run(c)
            resp = c.get("/api/runs", params={"status": "completed"})
            assert resp.status_code == 200
            assert resp.json()["pagination"]["total"] == 1

            resp = c.get("/api/runs", params={"status": "failed"})
            assert resp.json()["pagination"]["total"] == 0


class TestGetRun:
    def test_get_existing_run(self):
        with TestClient(app) as c:
            run_id = _create_run(c)
            resp = c.get(f"/api/runs/{run_id}")
            assert resp.status_code == 200
            body = resp.json()
            assert body["run_id"] == run_id
            assert body["status"] == "completed"
            assert body["detection_summary"]["total"] > 0
            assert len(body["detections"]) > 0
            coords = {
                (d["latitude"], d["longitude"])
                for d in body["detections"]
                if d.get("latitude") is not None
            }
            if len(body["detections"]) > 1:
                assert len(coords) > 1

    def test_get_nonexistent_run(self):
        with TestClient(app) as c:
            resp = c.get("/api/runs/nonexistent-id")
            assert resp.status_code == 404
            assert resp.json()["error"]["code"] == "RUN_NOT_FOUND"
