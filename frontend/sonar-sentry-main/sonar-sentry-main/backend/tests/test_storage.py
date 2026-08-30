import os
import tempfile
from pathlib import Path

from app.services.storage_service import StorageService


class TestStorageService:
    def setup_method(self):
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["UPLOAD_DIR"] = str(Path(self._tmp.name) / "uploads")
        os.environ["OUTPUT_DIR"] = str(Path(self._tmp.name) / "outputs")

    def teardown_method(self):
        self._tmp.cleanup()
        os.environ.pop("UPLOAD_DIR", None)
        os.environ.pop("OUTPUT_DIR", None)

    def test_save_upload(self):
        service = StorageService()
        path = service.save_upload(b"test content", "sonar.jpg")
        assert path.exists()
        assert path.suffix == ".jpg"
        assert path.read_bytes() == b"test content"

    def test_upload_dir_created(self):
        service = StorageService()
        assert service.upload_dir.exists()

    def test_output_dir_created(self):
        service = StorageService()
        assert service.output_dir.exists()

    def test_get_upload_path(self):
        service = StorageService()
        path = service.get_upload_path("test.jpg")
        assert path.name == "test.jpg"

    def test_file_exists(self):
        service = StorageService()
        path = service.save_upload(b"data", "test.bin")
        assert service.file_exists(path) is True

    def test_file_not_exists(self):
        service = StorageService()
        path = service.upload_dir / "nonexistent.bin"
        assert service.file_exists(path) is False
