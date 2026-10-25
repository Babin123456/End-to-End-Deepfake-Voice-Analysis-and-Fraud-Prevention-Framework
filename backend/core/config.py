import os
from dataclasses import dataclass
from functools import lru_cache

DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"


@dataclass(frozen=True)
class Settings:
    host: str
    port: int
    cors_origins: list[str]
    max_upload_size: int
    upload_chunk_size: int


def _split_origins(value: str) -> list[str]:
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    cors_origins = _split_origins(os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS))

    # FRONTEND_ORIGIN is the old single-origin variable, kept so existing
    # local setups keep working.
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "").strip().rstrip("/")
    if frontend_origin and frontend_origin not in cors_origins:
        cors_origins.append(frontend_origin)

    return Settings(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
        cors_origins=cors_origins,
        max_upload_size=int(os.getenv("MAX_UPLOAD_SIZE", str(25 * 1024 * 1024))),
        upload_chunk_size=int(os.getenv("UPLOAD_CHUNK_SIZE", str(1024 * 1024))),
    )
