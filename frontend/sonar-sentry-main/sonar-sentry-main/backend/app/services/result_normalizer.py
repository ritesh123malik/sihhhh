from __future__ import annotations

import uuid
from typing import Any

from app.schemas.detection import (
    BoundingBox,
    DetectionItem,
    DetectionSummary,
    RiskLevel,
)
from app.schemas.ml import Detection, PredictionResult


def _compute_risk_level(confidence: float) -> RiskLevel:
    if confidence >= 0.90:
        return RiskLevel.critical
    if confidence >= 0.80:
        return RiskLevel.high
    if confidence >= 0.65:
        return RiskLevel.medium
    return RiskLevel.low


class ResultNormalizer:
    """Converts raw model output into normalized application-level detections.

    This adapter layer ensures the frontend receives a consistent structure
    regardless of which ML model implementation is used.
    """

    def normalize(
        self,
        prediction_result: PredictionResult,
    ) -> tuple[list[DetectionItem], DetectionSummary]:
        items: list[DetectionItem] = []

        if prediction_result.detections:
            for det in prediction_result.detections:
                risk = _compute_risk_level(det.confidence)
                bbox_schema = None
                if det.bbox is not None:
                    bbox_schema = BoundingBox(
                        x=det.bbox.x,
                        y=det.bbox.y,
                        width=det.bbox.width,
                        height=det.bbox.height,
                    )
                items.append(
                    DetectionItem(
                        detection_id=str(uuid.uuid4()),
                        class_label=det.class_label,
                        confidence=det.confidence,
                        risk_level=risk,
                        bbox=bbox_schema,
                        depth_m=det.depth_m,
                        area_m2=det.area_m2,
                        position_info=det.position_info,
                    )
                )
        else:
            risk = _compute_risk_level(prediction_result.confidence)
            items.append(
                DetectionItem(
                    detection_id=str(uuid.uuid4()),
                    class_label=prediction_result.label,
                    confidence=prediction_result.confidence,
                    risk_level=risk,
                )
            )

        summary = self._build_summary(items)
        return items, summary

    def _build_summary(self, items: list[DetectionItem]) -> DetectionSummary:
        total = len(items)
        if total == 0:
            return DetectionSummary()

        high = sum(1 for d in items if d.risk_level in (RiskLevel.high, RiskLevel.critical))
        medium = sum(1 for d in items if d.risk_level == RiskLevel.medium)
        low = sum(1 for d in items if d.risk_level == RiskLevel.low)
        critical = sum(1 for d in items if d.risk_level == RiskLevel.critical)
        avg_conf = sum(d.confidence for d in items) / total

        return DetectionSummary(
            total=total,
            high_risk=high,
            medium_risk=medium,
            low_risk=low,
            critical_risk=critical,
            avg_confidence=round(avg_conf, 4),
        )
