import os
from functools import lru_cache


class Settings:
    """Application runtime configuration and environment variables."""

    def __init__(self):
        self.app_name: str = os.getenv("APP_NAME", "Deepfake Audio Detection & Fraud Prevention API")
        self.app_version: str = os.getenv("APP_VERSION", "1.0.0")
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

        # Server network settings
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))

        # CORS Allowed Origins
        frontend_origin = os.getenv("FRONTEND_ORIGIN")
        origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        if frontend_origin:
            origins.append(frontend_origin.rstrip("/"))
        extra_origins = os.getenv("ALLOWED_ORIGINS")
        if extra_origins:
            origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])
        self.allowed_origins: list[str] = list(set(origins))

        # File upload limits
        self.max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "25"))
        self.max_upload_size_bytes: int = self.max_upload_size_mb * 1024 * 1024
        self.upload_chunk_size: int = int(os.getenv("UPLOAD_CHUNK_SIZE", str(1024 * 1024)))

        # Supported audio formats
        self.supported_extensions: set[str] = {".wav", ".wave"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
