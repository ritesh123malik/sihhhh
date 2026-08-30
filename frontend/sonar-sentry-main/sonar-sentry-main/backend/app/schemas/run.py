from __future__ import annotations

from pydantic import BaseModel


class RunSummary(BaseModel):
    run_id: str
    mission_id: str
    filename: str
    status: str
    detection_count: int = 0
    file_size_bytes: int = 0
    latitude: float | None = None
    longitude: float | None = None
    created_at: str
    updated_at: str


class RunDetail(BaseModel):
    run_id: str
    mission_id: str
    filename: str
    file_size_bytes: int = 0
    status: str
    latitude: float | None = None
    longitude: float | None = None
    sonar_type: str | None = None
    resolution: str | None = None
    depth_min: float | None = None
    depth_max: float | None = None
    detection_count: int = 0
    avg_confidence: float | None = None
    model_name: str | None = None
    model_version: str | None = None
    model_provider: str | None = None
    created_at: str
    updated_at: str


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class RunListResponse(BaseModel):
    items: list[RunSummary]
    pagination: PaginationMeta
