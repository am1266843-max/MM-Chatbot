from datetime import datetime, timezone
from fastapi import APIRouter
from backend.core.database import check_db_health
from backend.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
def get_health():
    """Health check endpoint confirming backend service and database connectivity."""
    db_healthy = check_db_health()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected" if db_healthy else "disconnected",
        "app_env": settings.APP_ENV,
        "version": "1.0.0"
    }

