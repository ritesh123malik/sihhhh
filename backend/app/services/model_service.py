from abc import ABC, abstractmethod

from app.schemas.ml import ModelMetadata, PredictionResult, PreprocessedInput


class ModelService(ABC):
    """Abstract interface for model implementations.

    Implementations are framework-independent: they may wrap PyTorch,
    TensorFlow, ONNX Runtime, a random-forest, or any other backend.
    """

    @abstractmethod
    def load(self) -> None:
        """Initialise / load the model so that ``predict`` is ready."""

    @property
    @abstractmethod
    def is_loaded(self) -> bool:
        """Whether ``load()`` completed successfully."""

    @abstractmethod
    def predict(self, input_data: PreprocessedInput) -> PredictionResult:
        """Run inference on a single preprocessed input."""

    @abstractmethod
    def metadata(self) -> ModelMetadata:
        """Return descriptive metadata about the model."""
