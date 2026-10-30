from fastapi import APIRouter
from backend.core.config import settings
from backend.core.database import check_db_health, is_sqlite
from backend.services.ai.provider_factory import get_available_models
from backend.services.search.search_service import search_service
from backend.schemas.setting import SystemStatusResponse, ProviderStatus

router = APIRouter(prefix="/api/settings", tags=["Settings"])

@router.get("/status", response_model=SystemStatusResponse)
def get_system_status():
    """Retrieve full system operational status and provider availability."""
    db_ok = check_db_health()
    models = get_available_models()

    # Aggregate provider statuses
    seen_providers = set()
    providers: list[ProviderStatus] = []

    for m in models:
        p_name = m.provider
        if p_name not in seen_providers:
            seen_providers.add(p_name)
            is_cfg = settings.is_provider_configured(p_name)
            label = "Ready" if is_cfg else "API Key Needed"
            if p_name == "mock":
                label = "Active (Built-in)"
            elif p_name == "ollama":
                label = "Local (Default)"

            providers.append(ProviderStatus(
                name=p_name.capitalize(),
                configured=is_cfg,
                status_label=label,
                details=f"Provider {p_name}"
            ))

    return SystemStatusResponse(
        backend_status="Online",
        database_status="Connected" if db_ok else "Disconnected",
        database_type="SQLite (Local File)" if is_sqlite else "PostgreSQL",
        active_ai_provider=settings.AI_PROVIDER,
        providers=providers,
        search_configured=search_service.is_configured(),
        voice_configured=True, # Edge-TTS and gTTS are built-in & work without API keys
        rag_configured=True,
        upload_limit_mb=settings.MAX_UPLOAD_MB
    )

