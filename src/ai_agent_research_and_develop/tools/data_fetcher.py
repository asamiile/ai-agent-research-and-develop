"""
Data fetching tools for Research Agent
"""
import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class HackerNewsClient:
    """Fetch trending topics from Hacker News"""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    @classmethod
    def get_top_stories(cls, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch top stories from HN
        
        Returns list of stories with: id, title, url, score
        """
        try:
            # Get top story IDs
            response = requests.get(f"{cls.BASE_URL}/topstories.json", timeout=5)
            story_ids = response.json()[:limit]
            
            stories = []
            for story_id in story_ids:
                try:
                    story_response = requests.get(f"{cls.BASE_URL}/item/{story_id}.json", timeout=5)
                    story = story_response.json()
                    
                    if story.get("type") == "story" and story.get("title"):
                        stories.append({
                            "id": story.get("id"),
                            "title": story.get("title"),
                            "url": story.get("url", ""),
                            "score": story.get("score", 0),
                            "descendants": story.get("descendants", 0),
                            "source": "HackerNews"
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch HN story {story_id}: {e}")
                    continue
            
            return stories
        
        except Exception as e:
            logger.error(f"Failed to fetch HN stories: {e}")
            return []


class ProductHuntClient:
    """Fetch trending products from Product Hunt RSS"""
    
    FEED_URL = "https://www.producthunt.com/feed.xml"
    
    @classmethod
    def get_trending_products(cls, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Fetch trending products from Product Hunt via RSS
        
        Returns list of products with: title, link, description
        """
        try:
            feed = feedparser.parse(cls.FEED_URL)
            
            products = []
            for i, entry in enumerate(feed.entries[:limit], 1):
                products.append({
                    "rank": i,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "description": entry.get("summary", ""),
                    "source": "ProductHunt"
                })
            
            return products
        
        except Exception as e:
            logger.error(f"Failed to fetch Product Hunt feed: {e}")
            return []


class GitHubTrendingClient:
    """Fetch trending repositories from GitHub"""
    
    BASE_URL = "https://api.github.com/search/repositories"
    
    @classmethod
    def get_trending_repos(cls, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Fetch trending repos from GitHub using search API
        
        Returns list of repos with: name, url, stars, description
        """
        try:
            # Get repos trending in last week
            since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            query = f"created:>{since_date} stars:>100 language:python"
            
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": limit
            }
            
            response = requests.get(cls.BASE_URL, params=params, timeout=5)
            data = response.json()
            
            repos = []
            for repo in data.get("items", []):
                repos.append({
                    "name": repo.get("name", ""),
                    "full_name": repo.get("full_name", ""),
                    "url": repo.get("html_url", ""),
                    "stars": repo.get("stargazers_count", 0),
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "source": "GitHub"
                })
            
            return repos
        
        except Exception as e:
            logger.error(f"Failed to fetch GitHub trending repos: {e}")
            return []


def fetch_all_trends(hn_limit: int = 30, ph_limit: int = 20, gh_limit: int = 25) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch trends from all sources
    
    Returns dict with 'hacker_news', 'product_hunt', 'github_trending' keys
    """
    return {
        "hacker_news": HackerNewsClient.get_top_stories(hn_limit),
        "product_hunt": ProductHuntClient.get_trending_products(ph_limit),
        "github_trending": GitHubTrendingClient.get_trending_repos(gh_limit),
    }
