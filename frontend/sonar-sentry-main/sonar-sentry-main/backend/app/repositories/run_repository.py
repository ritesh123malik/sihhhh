from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.orm import Run


class RunRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create(self, **kwargs) -> Run:
        run = Run(**kwargs)
        self._db.add(run)
        self._db.commit()
        self._db.refresh(run)
        return run

    def get(self, run_id: str) -> Run | None:
        return self._db.query(Run).filter(Run.id == run_id).first()

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
    ) -> tuple[list[Run], int]:
        query = self._db.query(Run)
        if status:
            query = query.filter(Run.status == status)
        total = query.count()
        items = (
            query.order_by(Run.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return items, total

    def update(self, run_id: str, **kwargs) -> Run | None:
        run = self.get(run_id)
        if run is None:
            return None
        for key, value in kwargs.items():
            setattr(run, key, value)
        self._db.commit()
        self._db.refresh(run)
        return run

    def delete(self, run_id: str) -> bool:
        run = self.get(run_id)
        if run is None:
            return False
        file_path = run.file_path
        self._db.delete(run)
        self._db.commit()
        if file_path:
            from pathlib import Path

            path = Path(file_path)
            if path.is_file():
                path.unlink(missing_ok=True)
        return True
