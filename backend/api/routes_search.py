from fastapi import APIRouter
from backend.schemas.search import SearchQueryRequest, SearchResponse
from backend.services.search.search_service import search_service

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
async def perform_web_search(payload: SearchQueryRequest):
    """Perform real-time web search for current information and return structured sources."""
    return await search_service.search(payload.query, max_results=payload.max_results or 5)

