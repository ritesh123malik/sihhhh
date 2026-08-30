from __future__ import annotations

import csv
import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(tags=["anomalies"])


def _candidate_paths() -> list[Path]:
    paths: list[Path] = []
    here = Path(__file__).resolve()
    for parent in here.parents:
        paths.extend(
            [
                parent / "data" / "anomaly_report.csv",
                parent / "data" / "anomaly_report.json",
                parent / "backend" / "anomaly_report.csv",
                parent / "backend" / "anomaly_report.json",
                parent / "anomaly_report.csv",
                parent / "anomaly_report.json",
            ]
        )
    return paths


@router.get("/api/anomalies")
@router.get("/api/get_anomalies")
def get_anomalies() -> dict:
    seen: set[Path] = set()
    for path in _candidate_paths():
        resolved = path
        if resolved in seen:
            continue
        seen.add(resolved)
        if not resolved.is_file():
            continue
        if resolved.suffix.lower() == ".json":
            data = json.loads(resolved.read_text(encoding="utf-8"))
            return {"status": "success", "source": str(resolved), "data": data}
        with resolved.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        return {"status": "success", "source": str(resolved), "data": rows}
    return {"status": "error", "message": "Report not found."}
