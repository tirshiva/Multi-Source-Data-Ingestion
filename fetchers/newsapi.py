import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_newsapi(api_key: str, query: str) -> List[Dict[str, str]]:
    """
    Fetches top 10 articles from NewsAPI based on the given query.
    
    Args:
        api_key: NewsAPI API key for authentication
        query: Search query string for articles
        
    Returns:
        List of dictionaries with keys: title, content, source, url, fetched_at
        Returns empty list on failure
    """
    if not api_key:
        logger.error("API key is required but not provided")
        return []
    
    if not query:
        logger.error("Query parameter is required but not provided")
        return []
    
    # NewsAPI endpoint for searching articles
    url = "https://newsapi.org/v2/everything"
    
    params = {
        "q": query,
        "apiKey": api_key,
        "pageSize": 10,  # Fetch top 10 articles
        "sortBy": "relevancy"  # Sort by relevancy
    }
    
    headers = {
        "Accept": "application/json"
    }
    
    try:
        # Make request with 5 second timeout
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        # Handle rate limit (429)
        if response.status_code == 429:
            logger.error("Rate limit exceeded (429). Please wait before making more requests.")
            return []
        
        # Handle authentication error (401)
        if response.status_code == 401:
            logger.error("Authentication failed (401). Invalid API key.")
            return []
        
        # Handle other HTTP errors
        if response.status_code != 200:
            logger.error(f"HTTP error {response.status_code}: {response.text}")
            return []
        
        # Parse JSON response
        data = response.json()
        
        # Check if articles are present
        if data.get("status") != "ok":
            logger.error(f"NewsAPI returned status: {data.get('status')}, message: {data.get('message', 'Unknown error')}")
            return []
        
        articles = data.get("articles", [])
        
        # Format articles according to required structure
        formatted_articles = []
        fetched_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        for article in articles[:10]:  # Ensure we only take top 10
            url = article.get("url", "") or "N/A"
            formatted_article = {
                "title": article.get("title", ""),
                "content": article.get("content", "") or article.get("description", ""),
                "source": "newsapi",  # Fixed source value as per assignment
                "url": url,
                "fetched_at": fetched_at
            }
            formatted_articles.append(formatted_article)
        
        logger.info(f"Successfully fetched {len(formatted_articles)} articles for query: {query}")
        return formatted_articles
        
    except requests.exceptions.Timeout:
        logger.error("Request timed out after 5 seconds")
        return []
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return []
    
    except KeyError as e:
        logger.error(f"Unexpected response format: missing key {str(e)}")
        return []
    
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return []
