from abc import ABC, abstractmethod

from app.schemas.ml import PreprocessedInput


class Preprocessor(ABC):
    """Abstract interface for input preprocessing.

    A concrete implementation will eventually convert raw image bytes into
    whatever tensor representation the model requires.  This phase provides
    only the interface and a no-op placeholder.
    """

    @abstractmethod
    def process(self, raw_image_bytes: bytes) -> PreprocessedInput:
        """Convert raw image bytes into a ``PreprocessedInput``."""
