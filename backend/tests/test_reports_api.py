from fastapi.testclient import TestClient

from app.main import app

VALID_JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 100


def _create_report(client):
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
    detect_body = resp.json()
    report_resp = client.get("/api/reports")
    reports = report_resp.json()["items"]
    for r in reports:
        if r["run_id"] == detect_body["run_id"]:
            return r["report_id"]
    return None


class TestListReports:
    def test_empty_reports(self):
        with TestClient(app) as c:
            resp = c.get("/api/reports")
            assert resp.status_code == 200
            body = resp.json()
            assert body["items"] == []
            assert body["pagination"]["total"] == 0

    def test_reports_after_detect(self):
        with TestClient(app) as c:
            report_id = _create_report(c)
            assert report_id is not None
            resp = c.get("/api/reports")
            assert resp.status_code == 200
            assert resp.json()["pagination"]["total"] == 1

    def test_reports_pagination(self):
        with TestClient(app) as c:
            for _ in range(10):
                _create_report(c)
            resp = c.get("/api/reports", params={"page": 1, "page_size": 3})
            body = resp.json()
            assert len(body["items"]) == 3
            assert body["pagination"]["total"] == 10
            assert body["pagination"]["total_pages"] == 4

    def test_reports_status_filter(self):
        with TestClient(app) as c:
            _create_report(c)
            resp = c.get("/api/reports", params={"status": "completed"})
            assert resp.status_code == 200
            assert resp.json()["pagination"]["total"] == 1

            resp = c.get("/api/reports", params={"status": "flagged"})
            assert resp.json()["pagination"]["total"] == 0

    def test_reports_search(self):
        with TestClient(app) as c:
            _create_report(c)
            resp = c.get("/api/reports", params={"search": "Side-Scan"})
            assert resp.status_code == 200
            assert resp.json()["pagination"]["total"] == 1

            resp = c.get("/api/reports", params={"search": "nonexistent"})
            assert resp.json()["pagination"]["total"] == 0


class TestGetReport:
    def test_get_existing_report(self):
        with TestClient(app) as c:
            report_id = _create_report(c)
            assert report_id is not None
            resp = c.get(f"/api/reports/{report_id}")
            assert resp.status_code == 200
            body = resp.json()
            assert body["report_id"] == report_id
            assert body["status"] == "completed"
            assert body["anomaly_count"] > 0

    def test_export_report_csv(self):
        with TestClient(app) as c:
            report_id = _create_report(c)
            assert report_id is not None
            resp = c.get(f"/api/reports/{report_id}/export")
            assert resp.status_code == 200
            assert "text/csv" in resp.headers["content-type"]
            body = resp.text
            assert "latitude" in body
            assert "class_label" in body
            assert "12.9716" in body
        with TestClient(app) as c:
            resp = c.get("/api/reports/nonexistent-id")
            assert resp.status_code == 404
            assert resp.json()["error"]["code"] == "REPORT_NOT_FOUND"


class TestReportInstances:
    def test_threshold_creates_instance_not_new_report(self):
        with TestClient(app) as c:
            report_id = _create_report(c)
            run_id = c.get(f"/api/reports/{report_id}").json()["run_id"]
            before = c.get("/api/reports").json()["pagination"]["total"]
            resp = c.post(
                f"/api/runs/{run_id}/instances",
                json={"confidence_threshold": 80},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["kind"] == "instance"
            assert body["confidence_threshold"] == 80
            assert body["run_id"] == run_id
            after = c.get("/api/reports").json()
            assert after["pagination"]["total"] == before + 1
            kinds = {item["kind"] for item in after["items"]}
            assert "report" in kinds
            assert "instance" in kinds

    def test_same_threshold_reuses_instance(self):
        with TestClient(app) as c:
            report_id = _create_report(c)
            run_id = c.get(f"/api/reports/{report_id}").json()["run_id"]
            first = c.post(
                f"/api/runs/{run_id}/instances",
                json={"confidence_threshold": 70},
            ).json()
            second = c.post(
                f"/api/runs/{run_id}/instances",
                json={"confidence_threshold": 70},
            ).json()
            assert first["report_id"] == second["report_id"]


class TestDeletes:
    def test_delete_report(self):
        with TestClient(app) as c:
            report_id = _create_report(c)
            resp = c.delete(f"/api/reports/{report_id}")
            assert resp.status_code == 204
            assert c.get("/api/reports").json()["pagination"]["total"] == 0

    def test_delete_run(self):
        with TestClient(app) as c:
            report_id = _create_report(c)
            run_id = c.get(f"/api/reports/{report_id}").json()["run_id"]
            resp = c.delete(f"/api/runs/{run_id}")
            assert resp.status_code == 204
            assert c.get("/api/runs").json()["pagination"]["total"] == 0
            assert c.get("/api/reports").json()["pagination"]["total"] == 0
