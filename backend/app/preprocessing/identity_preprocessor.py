from app.preprocessing.base import Preprocessor
from app.schemas.ml import PreprocessedInput


class IdentityPreprocessor(Preprocessor):
    """No-op preprocessor that wraps raw bytes without transformation.

    Used as a placeholder until the real sonar preprocessing pipeline
    is defined in a later phase.
    """

    def process(self, raw_image_bytes: bytes) -> PreprocessedInput:
        if not isinstance(raw_image_bytes, bytes):
            raise TypeError("raw_image_bytes must be a bytes instance")
        if len(raw_image_bytes) == 0:
            raise ValueError("raw_image_bytes must not be empty")
        return PreprocessedInput(data=raw_image_bytes)
