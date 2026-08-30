from __future__ import annotations

from pydantic import BaseModel, Field


class ReportItem(BaseModel):
    report_id: str
    run_id: str
    mission_id: str
    mission_name: str
    filename: str
    scan_date: str
    anomaly_count: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    status: str
    confidence: float | None = None
    region: str | None = None
    kind: str = "report"
    parent_report_id: str | None = None
    confidence_threshold: int | None = None
    instance_id: str | None = None
    created_at: str
    updated_at: str


class ReportDetail(BaseModel):
    report_id: str
    run_id: str
    mission_id: str
    mission_name: str
    filename: str
    scan_date: str
    anomaly_count: int = 0
    high_risk_count: int = 0
    medium_risk_count: int = 0
    low_risk_count: int = 0
    status: str
    confidence: float | None = None
    region: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    sonar_type: str | None = None
    resolution: str | None = None
    depth_min: float | None = None
    depth_max: float | None = None
    model_name: str | None = None
    model_version: str | None = None
    created_at: str
    updated_at: str


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int


class ReportListResponse(BaseModel):
    items: list[ReportItem]
    pagination: PaginationMeta


class ReportInstanceCreate(BaseModel):
    confidence_threshold: int = Field(ge=0, le=100)
