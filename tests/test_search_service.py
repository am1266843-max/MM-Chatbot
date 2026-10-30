import pytest
from backend.services.search.search_service import WebSearchService

def test_search_service_config():
    service = WebSearchService()
    # DuckDuckGo is the default provider and does not require API keys
    assert service.is_configured() is True

@pytest.mark.asyncio
async def test_search_empty_query():
    service = WebSearchService()
    res = await service.search("")
    assert len(res.results) == 0

