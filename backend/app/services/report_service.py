from __future__ import annotations

import math
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.orm import Report as ReportORM
from app.models.orm import ReportInstance as ReportInstanceORM
from app.repositories.detection_repository import DetectionRepository
from app.repositories.report_repository import ReportRepository
from app.repositories.run_repository import RunRepository
from app.schemas.detection import DetectionItem, DetectionSummary
from app.schemas.report import PaginationMeta, ReportItem, ReportListResponse


class ReportService:
    def __init__(self, db: Session) -> None:
        self._repo = ReportRepository(db)
        self._db = db

    def create_report(
        self,
        run_id: str,
        mission_id: str,
        mission_name: str,
        filename: str,
        scan_date: str,
        detections: list[DetectionItem],
        summary: DetectionSummary,
        latitude: float | None = None,
        longitude: float | None = None,
        sonar_type: str | None = None,
        resolution: str | None = None,
        depth_min: float | None = None,
        depth_max: float | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
        region: str | None = None,
    ) -> ReportORM:
        return self._repo.create(
            run_id=run_id,
            mission_id=mission_id,
            mission_name=mission_name,
            filename=filename,
            scan_date=scan_date,
            anomaly_count=summary.total,
            high_risk_count=summary.high_risk,
            medium_risk_count=summary.medium_risk,
            low_risk_count=summary.low_risk,
            status="completed",
            confidence=round(summary.avg_confidence * 100, 1) if summary.total > 0 else None,
            region=region,
        )

    def get_report(self, report_id: str) -> ReportORM | None:
        return self._repo.get(report_id)

    def get_report_by_run(self, run_id: str) -> ReportORM | None:
        return self._repo.get_by_run_id(run_id)

    def list_reports(
        self,
        page: int = 1,
        page_size: int = 8,
        search: str | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        region: str | None = None,
        sort: str = "created_at",
        order: str = "desc",
    ) -> ReportListResponse:
        reports = self._repo.list_all_matching(
            search=search,
            status=None if status in (None, "instance") else status,
            date_from=date_from,
            date_to=date_to,
            region=region,
        )
        combined: list[ReportItem] = []
        if status != "instance":
            combined.extend(self._report_item(r) for r in reports)

        if status in (None, "instance"):
            parents = {r.id: r for r in reports}
            if not parents:
                for inst in self._repo.list_instances():
                    parent = self._repo.get(inst.report_id)
                    if parent:
                        parents[parent.id] = parent
            for inst in self._repo.list_instances():
                parent = parents.get(inst.report_id) or self._repo.get(inst.report_id)
                if parent is None:
                    continue
                item = self._instance_item(inst, parent)
                if search:
                    q = search.lower()
                    hay = f"{item.mission_name} {item.mission_id} {item.filename}".lower()
                    if q not in hay:
                        continue
                combined.append(item)

        reverse = order != "asc"
        combined.sort(key=lambda row: row.created_at, reverse=reverse)
        total = len(combined)
        start = (page - 1) * page_size
        paged = combined[start : start + page_size]
        total_pages = math.ceil(total / page_size) if total > 0 else 1

        return ReportListResponse(
            items=paged,
            pagination=PaginationMeta(
                page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
            ),
        )

    def update_status(self, report_id: str, status: str) -> ReportORM | None:
        return self._repo.update(report_id, status=status, updated_at=datetime.now(timezone.utc))

    def _report_item(self, r: ReportORM) -> ReportItem:
        return ReportItem(
            report_id=r.id,
            run_id=r.run_id,
            mission_id=r.mission_id,
            mission_name=r.mission_name,
            filename=r.filename,
            scan_date=r.scan_date,
            anomaly_count=r.anomaly_count,
            high_risk_count=r.high_risk_count,
            medium_risk_count=r.medium_risk_count,
            low_risk_count=r.low_risk_count,
            status=r.status,
            confidence=r.confidence,
            region=r.region,
            kind="report",
            created_at=r.created_at.isoformat() if r.created_at else "",
            updated_at=r.updated_at.isoformat() if r.updated_at else "",
        )

    def _instance_item(self, inst: ReportInstanceORM, parent: ReportORM) -> ReportItem:
        return ReportItem(
            report_id=inst.id,
            run_id=inst.run_id,
            mission_id=parent.mission_id,
            mission_name=f"{parent.mission_name} · {inst.confidence_threshold}% instance",
            filename=parent.filename,
            scan_date=parent.scan_date,
            anomaly_count=inst.anomaly_count,
            high_risk_count=inst.high_risk_count,
            medium_risk_count=inst.medium_risk_count,
            low_risk_count=inst.low_risk_count,
            status="instance",
            confidence=inst.avg_confidence,
            region=parent.region,
            kind="instance",
            parent_report_id=parent.id,
            confidence_threshold=inst.confidence_threshold,
            instance_id=inst.id,
            created_at=inst.created_at.isoformat() if inst.created_at else "",
            updated_at=inst.updated_at.isoformat() if inst.updated_at else "",
        )

    def create_threshold_instance(
        self, run_id: str, confidence_threshold: int
    ) -> ReportItem:
        existing = self._repo.get_instance_by_run_threshold(run_id, confidence_threshold)
        parent = self._repo.get_by_run_id(run_id)
        if parent is None:
            raise ValueError("No original report exists for this run.")

        detections = DetectionRepository(self._db).list_by_run(run_id)
        kept = [
            d
            for d in detections
            if round(d.confidence * 100) >= confidence_threshold
        ]
        high = sum(1 for d in kept if d.risk_level in ("high", "critical"))
        medium = sum(1 for d in kept if d.risk_level == "medium")
        low = sum(1 for d in kept if d.risk_level == "low")
        avg = (
            round(sum(d.confidence for d in kept) / len(kept) * 100, 1)
            if kept
            else None
        )

        if existing:
            existing.anomaly_count = len(kept)
            existing.high_risk_count = high
            existing.medium_risk_count = medium
            existing.low_risk_count = low
            existing.avg_confidence = avg
            existing.updated_at = datetime.now(timezone.utc)
            self._db.commit()
            self._db.refresh(existing)
            return self._instance_item(existing, parent)

        inst = self._repo.create_instance(
            report_id=parent.id,
            run_id=run_id,
            confidence_threshold=confidence_threshold,
            anomaly_count=len(kept),
            high_risk_count=high,
            medium_risk_count=medium,
            low_risk_count=low,
            avg_confidence=avg,
        )
        return self._instance_item(inst, parent)

    def delete_report_or_instance(self, item_id: str) -> bool:
        if self._repo.delete_instance(item_id):
            return True
        return self._repo.delete(item_id)

    def delete_run(self, run_id: str) -> bool:
        return RunRepository(self._db).delete(run_id)
