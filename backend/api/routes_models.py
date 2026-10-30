from fastapi import APIRouter
from backend.schemas.model import ModelListResponse
from backend.services.ai.provider_factory import get_available_models
from backend.core.config import settings

router = APIRouter(prefix="/api/models", tags=["Models"])

@router.get("", response_model=ModelListResponse)
def list_models():
    """List all supported AI models with live provider configuration flags."""
    models = get_available_models()
    return ModelListResponse(
        default_provider=settings.AI_PROVIDER,
        default_model=settings.AI_MODEL,
        models=models
    )

