import logging
from typing import List, Optional
import httpx
from backend.core.config import settings
from backend.schemas.search import SearchResultItem, SearchResponse

logger = logging.getLogger(__name__)

class WebSearchService:
    """Provides live web search results using DuckDuckGo or Tavily."""

    def __init__(self):
        self.provider = settings.SEARCH_PROVIDER.lower()
        self.tavily_key = settings.TAVILY_API_KEY

    def is_configured(self) -> bool:
        """DuckDuckGo requires no API keys, Tavily requires key."""
        if self.provider == "duckduckgo":
            return True
        elif self.provider == "tavily":
            return bool(self.tavily_key)
        return False

    async def search(self, query: str, max_results: int = 4) -> SearchResponse:
        """Perform search and return structured source items."""
        if not query or not query.strip():
            return SearchResponse(query=query, provider=self.provider, results=[])

        # If Tavily is requested and configured
        if self.provider == "tavily" and self.tavily_key:
            return await self._search_tavily(query, max_results)

        # Default: DuckDuckGo search
        return await self._search_duckduckgo(query, max_results)

    async def _search_duckduckgo(self, query: str, max_results: int) -> SearchResponse:
        try:
            from duckduckgo_search import DDGS
            results_list: List[SearchResultItem] = []

            # DDGS runs synchronously, we can invoke in worker or wrap cleanly
            with DDGS() as ddgs:
                ddg_gen = ddgs.text(query, max_results=max_results)
                for r in ddg_gen:
                    results_list.append(SearchResultItem(
                        title=r.get("title", "No Title"),
                        url=r.get("href", ""),
                        snippet=r.get("body", ""),
                        published_date=r.get("date")
                    ))

            return SearchResponse(
                query=query,
                provider="DuckDuckGo",
                results=results_list,
                is_simulated=False
            )
        except Exception as e:
            logger.warning(f"DuckDuckGo search error: {e}. Falling back to empty results.")
            return SearchResponse(
                query=query,
                provider="DuckDuckGo",
                results=[],
                is_simulated=False,
                message=f"Web search could not retrieve live results: {e}"
            )

    async def _search_tavily(self, query: str, max_results: int) -> SearchResponse:
        url = "https://api.tavily.com/search"
        payload = {
            "api_key": self.tavily_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic"
        }
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise RuntimeError(f"Tavily returned code {res.status_code}")
                data = res.json()
                items = []
                for item in data.get("results", []):
                    items.append(SearchResultItem(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        published_date=item.get("published_date")
                    ))
                return SearchResponse(
                    query=query,
                    provider="Tavily",
                    results=items,
                    is_simulated=False
                )
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return SearchResponse(
                query=query,
                provider="Tavily",
                results=[],
                is_simulated=False,
                message=f"Tavily search error: {e}"
            )

search_service = WebSearchService()

