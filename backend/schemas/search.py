from typing import List, Optional
from pydantic import BaseModel

class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    published_date: Optional[str] = None

class SearchQueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class SearchResponse(BaseModel):
    query: str
    provider: str
    results: List[SearchResultItem]
    is_simulated: bool = False
    message: Optional[str] = None

