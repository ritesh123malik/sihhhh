import uuid
from pathlib import Path

from app.config import get_settings


class StorageService:
    """Manages file storage for uploaded sonar files and detection outputs."""

    def __init__(self) -> None:
        settings = get_settings()
        self._upload_dir = Path(settings.upload_dir)
        self._output_dir = Path(settings.output_dir)
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def upload_dir(self) -> Path:
        return self._upload_dir

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    def save_upload(self, file_bytes: bytes, original_filename: str) -> Path:
        ext = Path(original_filename).suffix.lower() or ".bin"
        safe_name = f"{uuid.uuid4().hex}{ext}"
        dest = self._upload_dir / safe_name
        dest.write_bytes(file_bytes)
        return dest

    def get_upload_path(self, stored_name: str) -> Path:
        return self._upload_dir / stored_name

    def get_output_path(self, filename: str) -> Path:
        return self._output_dir / filename

    def file_exists(self, path: Path) -> bool:
        return path.exists() and path.is_file()
