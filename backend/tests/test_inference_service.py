from app.preprocessing.identity_preprocessor import IdentityPreprocessor
from app.services.mock_model_service import MockModelService
from app.services.inference_service import InferenceService
from app.schemas.ml import PredictionResult


class TestInferenceService:
    def setup_method(self):
        self.preprocessor = IdentityPreprocessor()
        self.model = MockModelService()
        self.service = InferenceService(
            preprocessor=self.preprocessor,
            model=self.model,
        )
        self.service.load()

    def test_is_model_loaded(self):
        assert self.service.is_model_loaded is True

    def test_calls_preprocessor_and_model(self):
        result = self.service.predict(b"\x89PNG")
        assert isinstance(result, PredictionResult)
        assert result.label in ("MOCK_CLASS_A", "MOCK_CLASS_B", "MOCK_CLASS_C")

    def test_metadata(self):
        meta = self.service.metadata()
        assert meta.name == "sonar-model"
        assert meta.provider == "mock"

    def test_same_input_same_result(self):
        a = self.service.predict(b"\x89PNG")
        b = self.service.predict(b"\x89PNG")
        assert a.label == b.label
        assert a.raw_scores == b.raw_scores

    def test_different_inputs_can_differ(self):
        a = self.service.predict(b"\x89PNG")
        b = self.service.predict(b"\xff\xd8\xff")
        assert a.label != b.label
