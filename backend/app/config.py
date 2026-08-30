from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    model_provider: str = "sonar"
    model_path: str = ""
    model_version: str = "colab-best"
    max_file_size_mb: int = 500
    frontend_origin: str = "http://localhost:5173"
    api_prefix: str = "/api"
    debug: bool = False

    database_url: str = "sqlite:///./sonar_sentry.db"
    upload_dir: str = str(Path(__file__).resolve().parent.parent / "data" / "uploads")
    output_dir: str = str(Path(__file__).resolve().parent.parent / "data" / "outputs")

    supabase_url: str = ""
    supabase_key: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""

    allowed_image_mimes: list[str] = ["image/jpeg", "image/png", "image/tiff"]
    allowed_sonar_types: list[str] = [
        "Side-Scan",
        "Multibeam",
        "Synthetic Aperture",
    ]
    allowed_resolutions: list[str] = ["0.1 m/px", "0.5 m/px", "1 m/px"]
    default_confidence_threshold: int = 20
    default_min_object_size: int = 10

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",  # Allow Vercel frontend
    ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
