import pytest

from app.config import Settings
from app.services.factory import create_inference_service
from app.services.inference_service import InferenceService


class TestFactory:
    def test_mock_provider(self):
        settings = Settings(model_provider="mock")
        service = create_inference_service(settings)
        assert isinstance(service, InferenceService)

    def test_unsupported_provider(self):
        settings = Settings(model_provider="nonexistent")
        with pytest.raises(ValueError, match="Unsupported MODEL_PROVIDER"):
            create_inference_service(settings)

    def test_mock_model_loaded_after_creation(self):
        settings = Settings(model_provider="mock")
        service = create_inference_service(settings)
        assert service.is_model_loaded is True
