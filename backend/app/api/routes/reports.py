from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.api.exceptions import ReportNotFoundError, RunNotFoundError
from app.database import get_db
from app.repositories.detection_repository import DetectionRepository
from app.repositories.run_repository import RunRepository
from app.schemas.report import ReportDetail, ReportInstanceCreate, ReportListResponse
from app.services.report_service import ReportService

router = APIRouter(tags=["reports"])


@router.get("/api/reports", response_model=ReportListResponse)
def list_reports(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=8, ge=1, le=100),
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    date_from: str | None = Query(default=None),
    date_to: str | None = Query(default=None),
    region: str | None = Query(default=None),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc"),
    db: Session = Depends(get_db),
) -> ReportListResponse:
    service = ReportService(db)
    return service.list_reports(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
        date_from=date_from,
        date_to=date_to,
        region=region,
        sort=sort,
        order=order,
    )


@router.get("/api/reports/{report_id}")
def get_report(report_id: str, db: Session = Depends(get_db)) -> dict:
    service = ReportService(db)
    report = service.get_report(report_id)
    if report is None:
        raise ReportNotFoundError()

    return {
        "report_id": report.id,
        "run_id": report.run_id,
        "mission_id": report.mission_id,
        "mission_name": report.mission_name,
        "filename": report.filename,
        "scan_date": report.scan_date,
        "anomaly_count": report.anomaly_count,
        "high_risk_count": report.high_risk_count,
        "medium_risk_count": report.medium_risk_count,
        "low_risk_count": report.low_risk_count,
        "status": report.status,
        "confidence": report.confidence,
        "region": report.region,
        "created_at": report.created_at.isoformat() if report.created_at else "",
        "updated_at": report.updated_at.isoformat() if report.updated_at else "",
    }


@router.get("/api/reports/{report_id}/export")
def export_report(report_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    service = ReportService(db)
    report = service.get_report(report_id)
    if report is None:
        raise ReportNotFoundError()

    run = RunRepository(db).get(report.run_id)
    if run is None:
        raise RunNotFoundError()

    detections = DetectionRepository(db).list_by_run(run.id)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "mission_id",
            "run_id",
            "filename",
            "latitude",
            "longitude",
            "class_label",
            "confidence_pct",
            "risk_level",
            "depth_m",
            "area_m2",
            "bbox_x",
            "bbox_y",
            "bbox_width",
            "bbox_height",
        ]
    )
    if detections:
        for det in detections:
            writer.writerow(
                [
                    report.mission_id,
                    run.id,
                    report.filename,
                    run.latitude,
                    run.longitude,
                    det.class_label,
                    round(det.confidence * 100),
                    det.risk_level,
                    det.depth_m,
                    det.area_m2,
                    det.bbox_x,
                    det.bbox_y,
                    det.bbox_width,
                    det.bbox_height,
                ]
            )
    else:
        writer.writerow(
            [
                report.mission_id,
                run.id,
                report.filename,
                run.latitude,
                run.longitude,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            ]
        )

    buffer.seek(0)
    filename = f"{report.mission_id}-detections.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.delete("/api/reports/{report_id}")
def delete_report(report_id: str, db: Session = Depends(get_db)) -> Response:
    deleted = ReportService(db).delete_report_or_instance(report_id)
    if not deleted:
        raise ReportNotFoundError()
    return Response(status_code=204)
