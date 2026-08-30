from app.schemas.ml import BBox, Detection, PredictionResult
from app.services.result_normalizer import ResultNormalizer


class TestResultNormalizer:
    def setup_method(self):
        self.normalizer = ResultNormalizer()

    def test_normalize_single_detection(self):
        result = PredictionResult(
            label="Shipwreck",
            confidence=0.85,
            raw_scores={"Shipwreck": 0.85, "Debris": 0.1},
            detections=[
                Detection(class_label="Shipwreck", confidence=0.85),
            ],
        )
        items, summary = self.normalizer.normalize(result)
        assert len(items) == 1
        assert items[0].class_label == "Shipwreck"
        assert items[0].confidence == 0.85
        assert summary.total == 1

    def test_normalize_multiple_detections(self):
        result = PredictionResult(
            label="MOCK_CLASS_A",
            confidence=0.75,
            raw_scores={},
            detections=[
                Detection(class_label="Shipwreck", confidence=0.95),
                Detection(class_label="Debris", confidence=0.82),
                Detection(class_label="Rock Formation", confidence=0.60),
            ],
        )
        items, summary = self.normalizer.normalize(result)
        assert len(items) == 3
        assert summary.total == 3
        assert summary.high_risk == 2
        assert summary.low_risk == 1

    def test_risk_levels(self):
        result = PredictionResult(
            label="X",
            confidence=0.5,
            raw_scores={},
            detections=[
                Detection(class_label="A", confidence=0.95),
                Detection(class_label="B", confidence=0.85),
                Detection(class_label="C", confidence=0.70),
                Detection(class_label="D", confidence=0.50),
            ],
        )
        items, summary = self.normalizer.normalize(result)
        assert items[0].risk_level.value == "critical"
        assert items[1].risk_level.value == "high"
        assert items[2].risk_level.value == "medium"
        assert items[3].risk_level.value == "low"

    def test_bbox_preserved(self):
        result = PredictionResult(
            label="X",
            confidence=0.9,
            raw_scores={},
            detections=[
                Detection(
                    class_label="Shipwreck",
                    confidence=0.9,
                    bbox=BBox(x=10, y=20, width=100, height=50),
                    depth_m=25.3,
                    area_m2=5.0,
                ),
            ],
        )
        items, _ = self.normalizer.normalize(result)
        assert items[0].bbox is not None
        assert items[0].bbox.x == 10
        assert items[0].depth_m == 25.3
        assert items[0].area_m2 == 5.0

    def test_fallback_to_single_label_when_no_detections(self):
        result = PredictionResult(
            label="Debris",
            confidence=0.75,
            raw_scores={"Debris": 0.75},
            detections=[],
        )
        items, summary = self.normalizer.normalize(result)
        assert len(items) == 1
        assert items[0].class_label == "Debris"
        assert summary.total == 1

    def test_empty_summary(self):
        from app.schemas.detection import DetectionSummary

        normalizer = ResultNormalizer()
        result = PredictionResult(label="X", confidence=0.5, raw_scores={})
        items, summary = normalizer.normalize(result)
        assert summary.total == 1
