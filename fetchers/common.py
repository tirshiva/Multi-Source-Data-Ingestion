from datetime import datetime
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def normalize_article(raw_data: Dict[str, Any], source: str) -> Dict[str, str]:
    """
    Normalizes raw article data into a consistent output format.
    
    This function ensures all articles follow the standard format with required fields:
    title, content, source, url, and fetched_at. Missing fields are handled gracefully
    by providing default empty strings, and a timestamp is added if missing.
    
    Args:
        raw_data: Dictionary containing raw article data with potentially varying keys.
                 Common keys might include: title, content, description, url, source, etc.
        source: Source identifier for the article (e.g., "NewsAPI", "CSV", domain name).
                This will override any source field in raw_data.
        
    Returns:
        Dictionary with standardized keys:
        - title: Article title (str)
        - content: Article content/body (str)
        - source: Article source identifier (str)
        - url: Article URL (str)
        - fetched_at: ISO 8601 timestamp (str)
        
    Example:
        >>> raw = {"title": "Test", "description": "Content here", "url": "https://example.com"}
        >>> normalize_article(raw, "NewsAPI")
        {
            "title": "Test",
            "content": "Content here",
            "source": "NewsAPI",
            "url": "https://example.com",
            "fetched_at": "2024-01-01T12:00:00.123456"
        }
    """
    if not isinstance(raw_data, dict):
        logger.warning(f"raw_data is not a dictionary, got {type(raw_data)}. Returning empty article.")
        raw_data = {}
    
    if not isinstance(source, str):
        logger.warning(f"source is not a string, got {type(source)}. Using empty string.")
        source = str(source) if source else ""
    
    # Extract title with fallback options
    title = (
        raw_data.get("title") or
        raw_data.get("headline") or
        raw_data.get("name") or
        ""
    )
    # Ensure title is a string
    title = str(title) if title is not None else ""
    
    # Extract content with fallback options (description, body, text, etc.)
    content = (
        raw_data.get("content") or
        raw_data.get("description") or
        raw_data.get("body") or
        raw_data.get("text") or
        raw_data.get("summary") or
        ""
    )
    # Ensure content is a string
    content = str(content) if content is not None else ""
    
    # Extract URL with fallback options
    url = (
        raw_data.get("url") or
        raw_data.get("link") or
        raw_data.get("webUrl") or
        raw_data.get("article_url") or
        ""
    )
    # Ensure url is a string
    url = str(url) if url is not None else ""
    
    # Use provided source parameter (overrides any source in raw_data)
    # Ensure source is a string
    source = str(source) if source else ""
    
    # Handle fetched_at timestamp
    fetched_at = raw_data.get("fetched_at") or raw_data.get("publishedAt") or raw_data.get("published_at")
    
    # If fetched_at exists, ensure it's a string and valid ISO 8601 format
    if fetched_at:
        try:
            # If it's already a string, try to parse and reformat to ensure ISO 8601
            if isinstance(fetched_at, str):
                # Try to parse and reformat to ensure proper ISO 8601
                try:
                    dt = datetime.fromisoformat(fetched_at.replace('Z', '+00:00'))
                    fetched_at = dt.isoformat()
                except (ValueError, AttributeError):
                    # If parsing fails, use as-is if it looks like a timestamp
                    fetched_at = str(fetched_at)
            elif isinstance(fetched_at, datetime):
                fetched_at = fetched_at.isoformat()
            else:
                fetched_at = str(fetched_at)
        except Exception as e:
            logger.warning(f"Could not parse fetched_at timestamp: {str(e)}. Generating new timestamp.")
            fetched_at = None
    
    # Generate new timestamp if missing or invalid
    if not fetched_at:
        fetched_at = datetime.now().isoformat()
    
    # Build normalized article dictionary
    normalized_article = {
        "title": title,
        "content": content,
        "source": source,
        "url": url,
        "fetched_at": fetched_at
    }
    
    return normalized_article
