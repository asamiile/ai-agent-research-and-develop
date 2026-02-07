"""This is the tools package for the AI Agent Research and Development project."""

from .data_fetcher import (
    HackerNewsClient,
    ProductHuntClient,
    GitHubTrendingClient,
    fetch_all_trends,
)
from .web_fetcher import (
    WebContentFetcher,
    NewsSourceFetcher,
    fetch_url_content,
)

__all__ = [
    "HackerNewsClient",
    "ProductHuntClient",
    "GitHubTrendingClient",
    "fetch_all_trends",
    "WebContentFetcher",
    "NewsSourceFetcher",
    "fetch_url_content",
]
