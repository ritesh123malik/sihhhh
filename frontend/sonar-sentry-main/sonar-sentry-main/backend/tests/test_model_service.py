import pytest

from app.services.model_service import ModelService
from app.services.mock_model_service import MockModelService
from app.schemas.ml import ModelMetadata, PredictionResult, PreprocessedInput


class TestModelServiceInterface:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            ModelService()  # type: ignore[abstract]


class TestMockModelService:
    def setup_method(self):
        self.service = MockModelService()

    def test_load_succeeds(self):
        self.service.load()
        assert self.service.is_loaded is True

    def test_not_loaded_before_load(self):
        assert self.service.is_loaded is False

    def test_metadata_returns_model_metadata(self):
        meta = self.service.metadata()
        assert isinstance(meta, ModelMetadata)
        assert meta.name == "sonar-model"
        assert meta.version == "development"
        assert meta.provider == "mock"

    def test_predict_raises_if_not_loaded(self):
        inp = PreprocessedInput(data=b"test")
        with pytest.raises(RuntimeError, match="not been loaded"):
            self.service.predict(inp)

    def test_predict_returns_prediction_result(self):
        self.service.load()
        result = self.service.predict(PreprocessedInput(data=b"\x89PNG"))
        assert isinstance(result, PredictionResult)
        assert result.label in ("MOCK_CLASS_A", "MOCK_CLASS_B", "MOCK_CLASS_C")
        assert 0.0 <= result.confidence <= 1.0
        assert isinstance(result.raw_scores, dict)
        assert len(result.raw_scores) == 3

    def test_same_input_same_prediction(self):
        self.service.load()
        a = self.service.predict(PreprocessedInput(data=b"\x89PNG"))
        b = self.service.predict(PreprocessedInput(data=b"\x89PNG"))
        assert a.label == b.label
        assert a.confidence == b.confidence
        assert a.raw_scores == b.raw_scores

    def test_different_inputs_can_differ(self):
        self.service.load()
        a = self.service.predict(PreprocessedInput(data=b"\x89PNG"))
        b = self.service.predict(PreprocessedInput(data=b"\xff\xd8\xff"))
        assert a.label != b.label
