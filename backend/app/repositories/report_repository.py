from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.orm import Report, ReportInstance


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, **kwargs) -> Report:
        report = Report(**kwargs)
        self._db.add(report)
        self._db.commit()
        self._db.refresh(report)
        return report

    def get(self, report_id: str) -> Report | None:
        return self._db.query(Report).filter(Report.id == report_id).first()

    def get_by_run_id(self, run_id: str) -> Report | None:
        return self._db.query(Report).filter(Report.run_id == run_id).first()

    def list(
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
    ) -> tuple[list[Report], int]:
        query = self._db.query(Report)

        if search:
            like_pattern = f"%{search}%"
            query = query.filter(
                (Report.mission_name.ilike(like_pattern))
                | (Report.mission_id.ilike(like_pattern))
                | (Report.filename.ilike(like_pattern))
            )
        if status:
            query = query.filter(Report.status == status)
        if date_from:
            query = query.filter(Report.scan_date >= date_from)
        if date_to:
            query = query.filter(Report.scan_date <= date_to)
        if region:
            query = query.filter(Report.region == region)

        total = query.count()

        sort_column = getattr(Report, sort, Report.created_at)
        if order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def list_all_matching(
        self,
        search: str | None = None,
        status: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        region: str | None = None,
    ) -> list[Report]:
        items, _total = self.list(
            page=1,
            page_size=10_000,
            search=search,
            status=status,
            date_from=date_from,
            date_to=date_to,
            region=region,
            sort="created_at",
            order="desc",
        )
        return items

    def update(self, report_id: str, **kwargs) -> Report | None:
        report = self.get(report_id)
        if report is None:
            return None
        for key, value in kwargs.items():
            setattr(report, key, value)
        self._db.commit()
        self._db.refresh(report)
        return report

    def delete(self, report_id: str) -> bool:
        report = self.get(report_id)
        if report is None:
            return False
        self._db.delete(report)
        self._db.commit()
        return True

    def create_instance(self, **kwargs) -> ReportInstance:
        instance = ReportInstance(**kwargs)
        self._db.add(instance)
        self._db.commit()
        self._db.refresh(instance)
        return instance

    def get_instance(self, instance_id: str) -> ReportInstance | None:
        return (
            self._db.query(ReportInstance).filter(ReportInstance.id == instance_id).first()
        )

    def get_instance_by_run_threshold(
        self, run_id: str, confidence_threshold: int
    ) -> ReportInstance | None:
        return (
            self._db.query(ReportInstance)
            .filter(
                ReportInstance.run_id == run_id,
                ReportInstance.confidence_threshold == confidence_threshold,
            )
            .first()
        )

    def list_instances(self, run_id: str | None = None) -> list[ReportInstance]:
        query = self._db.query(ReportInstance)
        if run_id:
            query = query.filter(ReportInstance.run_id == run_id)
        return query.order_by(ReportInstance.created_at.desc()).all()

    def delete_instance(self, instance_id: str) -> bool:
        instance = self.get_instance(instance_id)
        if instance is None:
            return False
        self._db.delete(instance)
        self._db.commit()
        return True
