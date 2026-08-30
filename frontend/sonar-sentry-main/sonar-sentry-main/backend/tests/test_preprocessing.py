import pytest

from app.preprocessing.base import Preprocessor
from app.preprocessing.identity_preprocessor import IdentityPreprocessor
from app.schemas.ml import PreprocessedInput


class TestPreprocessorInterface:
    def test_is_abstract(self):
        with pytest.raises(TypeError):
            Preprocessor()  # type: ignore[abstract]


class TestIdentityPreprocessor:
    def setup_method(self):
        self.preprocessor = IdentityPreprocessor()

    def test_returns_preprocessed_input(self):
        result = self.preprocessor.process(b"\x89PNG")
        assert isinstance(result, PreprocessedInput)

    def test_wraps_bytes_without_transformation(self):
        raw = b"\x89PNG\r\n\x1a\n"
        result = self.preprocessor.process(raw)
        assert result.data == raw

    def test_rejects_non_bytes(self):
        with pytest.raises(TypeError):
            self.preprocessor.process("not bytes")  # type: ignore[arg-type]

    def test_rejects_empty_bytes(self):
        with pytest.raises(ValueError):
            self.preprocessor.process(b"")
