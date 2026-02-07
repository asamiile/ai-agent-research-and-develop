"""
Web content fetcher using requests and basic HTML parsing
For Raspberry Pi compatibility, using minimal dependencies
"""
import requests
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class WebContentFetcher:
    """
    Simple web content fetcher optimized for Pi
    Uses requests library and basic string parsing instead of heavy dependencies
    """
    
    TIMEOUT = 10
    MAX_CONTENT_LENGTH = 50000  # 50KB max per page
    
    @classmethod
    def fetch_content(cls, url: str) -> Optional[str]:
        """
        Fetch text content from URL
        
        Returns: text content or None if failed
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux arm64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, timeout=cls.TIMEOUT, headers=headers)
            response.raise_for_status()
            
            # Return text content up to MAX_CONTENT_LENGTH
            return response.text[:cls.MAX_CONTENT_LENGTH]
        
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None
    
    @classmethod
    def extract_text_snippets(cls, content: str, snippet_length: int = 200) -> List[str]:
        """
        Extract text snippets from HTML content
        Simple approach: remove script/style tags, split by paragraphs
        """
        if not content:
            return []
        
        # Simple HTML tag removal
        import re
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        
        # Split into sentences and create snippets
        sentences = content.split('.')
        snippets = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:
                snippets.append(sentence[:snippet_length])
        
        return snippets[:5]  # Return top 5 snippets


class NewsSourceFetcher:
    """
    Fetch non-technical news and insights relevant to business/tech trends
    """
    
    # Free news APIs and RSS sources
    NEWS_SOURCES = [
        {
            "name": "Tech Crunch RSS",
            "type": "rss",
            "url": "https://techcrunch.com/feed/",
        },
        {
            "name": "The Verge",
            "type": "rss", 
            "url": "https://www.theverge.com/rss/index.xml"
        },
        {
            "name": "Indie Hackers",
            "type": "rss",
            "url": "https://www.indiehackers.com/feed.xml"
        }
    ]
    
    @classmethod
    def fetch_tech_news(cls) -> List[Dict[str, Any]]:
        """
        Fetch tech news from RSS feeds
        """
        import feedparser
        
        all_news = []
        for source in cls.NEWS_SOURCES:
            try:
                feed = feedparser.parse(source["url"])
                for entry in feed.entries[:5]:
                    all_news.append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "source": source["name"],
                        "published": entry.get("published", ""),
                    })
            except Exception as e:
                logger.warning(f"Failed to fetch from {source['name']}: {e}")
        
        return all_news


def fetch_url_content(url: str) -> Optional[Dict[str, Any]]:
    """
    Fetch content from a URL and return structured data
    
    Returns dict with: url, title, snippets, fetched_at
    """
    content = WebContentFetcher.fetch_content(url)
    
    if not content:
        return None
    
    snippets = WebContentFetcher.extract_text_snippets(content)
    
    # Try to extract title from content
    title = "Content from " + url.split('/')[2]
    
    return {
        "url": url,
        "title": title,
        "snippets": snippets,
        "fetched_at": str(__import__('datetime').datetime.now()),
    }
