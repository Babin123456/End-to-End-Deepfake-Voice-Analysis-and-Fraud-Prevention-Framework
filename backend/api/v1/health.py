import platform
import time

from fastapi import APIRouter

from core.config import get_settings

router = APIRouter()

_started_at = time.monotonic()


@router.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "uptime_seconds": round(time.monotonic() - _started_at, 2),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "upload_limits": {
            "max_upload_size": settings.max_upload_size,
            "upload_chunk_size": settings.upload_chunk_size,
        },
    }
