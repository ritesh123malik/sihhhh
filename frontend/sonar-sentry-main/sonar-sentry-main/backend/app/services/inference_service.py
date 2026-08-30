from __future__ import annotations

from app.preprocessing.base import Preprocessor
from app.schemas.ml import ModelMetadata, PredictionResult, PreprocessedInput
from app.services.model_service import ModelService


class InferenceService:
    """Orchestrates preprocessing and model inference.

    The API layer calls ``predict(raw_bytes)`` without knowing the details
    of either preprocessing or model execution.
    """

    def __init__(self, preprocessor: Preprocessor, model: ModelService) -> None:
        self._preprocessor = preprocessor
        self._model = model

    def load(self) -> None:
        """Load the underlying model."""
        self._model.load()

    @property
    def is_model_loaded(self) -> bool:
        return self._model.is_loaded

    def predict(self, raw_image_bytes: bytes) -> PredictionResult:
        preprocessed: PreprocessedInput = self._preprocessor.process(raw_image_bytes)
        return self._model.predict(preprocessed)

    def metadata(self) -> ModelMetadata:
        return self._model.metadata()
