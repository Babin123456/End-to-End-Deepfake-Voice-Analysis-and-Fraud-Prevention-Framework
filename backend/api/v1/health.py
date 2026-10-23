import time
import platform
from fastapi import APIRouter

try:
    from core.config import get_settings
except ImportError:
    from backend.core.config import get_settings

router = APIRouter(prefix="/api/v1", tags=["System Health"])
_START_TIME = time.time()


@router.get("/health")
def health_check():
    """
    Health check endpoint for container orchestrators, load balancers,
    and monitoring agents.
    """
    settings = get_settings()
    uptime_seconds = round(time.time() - _START_TIME, 1)

    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": uptime_seconds,
        "system": {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
        },
        "limits": {
            "max_upload_size_mb": settings.max_upload_size_mb,
            "supported_extensions": list(settings.supported_extensions),
        },
    }
