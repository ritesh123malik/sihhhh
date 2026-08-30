import hashlib
import uuid

from app.schemas.ml import BBox, Detection, ModelMetadata, PredictionResult, PreprocessedInput
from app.services.model_service import ModelService

_MOCK_LABELS = ("MOCK_CLASS_A", "MOCK_CLASS_B", "MOCK_CLASS_C")
_MOCK_DETECT_LABELS = ("Shipwreck", "Debris", "Fishing Net", "Rock Formation", "Metal Fragment", "Container")


class MockModelService(ModelService):
    """Deterministic mock model for development and testing.

    Produces reproducible predictions derived from a hash of the input
    bytes.  The labels are intentionally meaningless — this model is
    **not** intended to perform any real sonar analysis.

    Generates multiple mock detections to exercise the full detection
    pipeline including result normalization and persistence.
    """

    def __init__(self) -> None:
        self._loaded = False

    def load(self) -> None:
        self._loaded = True

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def predict(self, input_data: PreprocessedInput) -> PredictionResult:
        if not self._loaded:
            raise RuntimeError("Model has not been loaded. Call load() first.")

        raw = input_data.data
        if isinstance(raw, bytes):
            digest = hashlib.sha256(raw).hexdigest()
        else:
            digest = hashlib.sha256(str(raw).encode()).hexdigest()

        index = int(digest, 16) % len(_MOCK_LABELS)
        label = _MOCK_LABELS[index]

        scores = {
            lbl: (1.0 if lbl == label else 0.1) for lbl in _MOCK_LABELS
        }

        detections = self._generate_mock_detections(digest)

        return PredictionResult(
            label=label,
            confidence=0.75,
            raw_scores=scores,
            detections=detections,
        )

    def _generate_mock_detections(self, digest: str) -> list[Detection]:
        seed = int(digest[:8], 16)
        num_detections = 3 + (seed % 5)
        detections: list[Detection] = []

        for i in range(num_detections):
            det_seed = int(digest[(i * 2) : (i * 2 + 8)], 16) if (i * 2 + 8) <= len(digest) else seed + i
            label = _MOCK_DETECT_LABELS[det_seed % len(_MOCK_DETECT_LABELS)]
            confidence = round(0.55 + (det_seed % 40) / 100.0, 2)
            confidence = min(confidence, 0.99)

            x = float(det_seed % 800)
            y = float((det_seed * 7) % 600)
            w = float(40 + (det_seed % 120))
            h = float(30 + (det_seed % 90))

            depth = round(2.0 + (det_seed % 400) / 10.0, 1)
            area = round(w * h / 100.0, 1)

            detections.append(
                Detection(
                    class_label=label,
                    confidence=confidence,
                    bbox=BBox(x=x, y=y, width=w, height=h),
                    depth_m=depth,
                    area_m2=area,
                    position_info=f"MOCK_POSITION_{i + 1}",
                )
            )

        return detections

    def metadata(self) -> ModelMetadata:
        return ModelMetadata(
            name="sonar-model",
            version="development",
            provider="mock",
        )
