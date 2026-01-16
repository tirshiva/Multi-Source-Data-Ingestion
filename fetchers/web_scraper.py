import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from typing import List, Dict
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_website(url: str) -> List[Dict[str, str]]:
    """
    Scrapes articles from a webpage and extracts article information.
    
    Args:
        url: URL of the webpage to scrape
        
    Returns:
        List of dictionaries with keys: title, content, source, url, fetched_at
        Returns empty list on failure
    """
    if not url:
        logger.error("URL is required but not provided")
        return []
    
    # Extract domain name from URL for source field
    try:
        parsed_url = urlparse(url)
        source = parsed_url.netloc or parsed_url.path.split('/')[0] if parsed_url.path else ""
        if not source:
            source = url
    except Exception as e:
        logger.warning(f"Could not parse URL for domain extraction: {str(e)}")
        source = url
    
    # Headers with User-Agent to avoid blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Make request with 10 second timeout
        response = requests.get(url, headers=headers, timeout=10)
        
        # Handle 404 error
        if response.status_code == 404:
            logger.error(f"Page not found (404): {url}")
            return []
        
        # Handle other HTTP errors
        if response.status_code != 200:
            logger.error(f"HTTP error {response.status_code} for URL: {url}")
            return []
        
        # Parse HTML with BeautifulSoup
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Failed to parse HTML content: {str(e)}")
            return []
        
        # Extract title from h1 or h2
        title = ""
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text(strip=True)
        else:
            h2_tag = soup.find('h2')
            if h2_tag:
                title = h2_tag.get_text(strip=True)
        
        if not title:
            logger.warning(f"No title found (h1 or h2) for URL: {url}")
            # Try alternative: look for title tag or meta title
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text(strip=True)
            else:
                meta_title = soup.find('meta', property='og:title')
                if meta_title:
                    title = meta_title.get('content', '')
        
        # Extract content from paragraphs
        paragraphs = soup.find_all('p')
        content_parts = []
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:  # Only add non-empty paragraphs
                content_parts.append(text)
        
        content = " ".join(content_parts)
        
        # If no paragraphs found, try to get body text
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(strip=True, separator=' ')
        
        if not content:
            logger.warning(f"No content found (paragraphs) for URL: {url}")
        
        # Format article according to required structure
        fetched_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        
        formatted_article = {
            "title": title,
            "content": content,
            "source": source,  # Domain name from URL
            "url": url,
            "fetched_at": fetched_at
        }
        
        logger.info(f"Successfully scraped article from URL: {url}")
        return [formatted_article]
        
    except requests.exceptions.Timeout:
        logger.error(f"Connection timed out after 10 seconds for URL: {url}")
        return []
    
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error for URL {url}: {str(e)}")
        return []
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for URL {url}: {str(e)}")
        return []
    
    except Exception as e:
        logger.error(f"Unexpected error occurred while scraping {url}: {str(e)}")
        return []
