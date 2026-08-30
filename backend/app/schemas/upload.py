from __future__ import annotations

from pydantic import BaseModel, Field


class UploadMetadata(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    sonar_type: str = Field(..., min_length=1)
    resolution: str = Field(..., min_length=1)
    depth_min: float = Field(..., ge=0.0)
    depth_max: float = Field(..., gt=0.0)


class DetectionSettings(BaseModel):
    confidence_threshold: int = Field(default=78, ge=50, le=95)
    selected_classes: list[str] = Field(default_factory=lambda: ["Debris", "Shipwreck"])
    min_object_size: int = Field(default=40, ge=10, le=200)
