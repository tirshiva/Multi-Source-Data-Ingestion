import json
import os
import logging
from typing import List, Dict
from fetchers.newsapi import fetch_newsapi
from fetchers.csv_reader import read_csv
from fetchers.web_scraper import scrape_website

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main function that runs all fetchers, combines results, and saves to JSON.
    """
    all_articles: List[Dict[str, str]] = []

    # Fetch articles from NewsAPI
    logger.info("Starting NewsAPI fetch...")
    try:
        # You can set these via environment variables or modify as needed
        api_key = os.getenv("NEWSAPI_KEY", "")
        query = os.getenv("NEWSAPI_QUERY", "technology")

        if api_key:
            newsapi_articles = fetch_newsapi(api_key, query)
            all_articles.extend(newsapi_articles)
            logger.info(f"Fetched {len(newsapi_articles)} articles from NewsAPI")
        else:
            logger.warning("NewsAPI key not provided. Skipping NewsAPI fetch.")
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {str(e)}")

    # Read articles from CSV
    logger.info("Starting CSV read...")
    try:
        csv_file_path = os.getenv("CSV_FILE_PATH", "sample_data.csv")

        if os.path.exists(csv_file_path):
            csv_articles = read_csv(csv_file_path)
            all_articles.extend(csv_articles)
            logger.info(f"Read {len(csv_articles)} articles from CSV")
        else:
            logger.warning(f"CSV file not found at {csv_file_path}. Skipping CSV read.")
    except Exception as e:
        logger.error(f"Error reading CSV: {str(e)}")

    # Scrape articles from website
    logger.info("Starting website scrape...")
    try:
        website_url = os.getenv("WEBSITE_URL", "")

        if website_url:
            scraped_articles = scrape_website(website_url)
            all_articles.extend(scraped_articles)
            logger.info(f"Scraped {len(scraped_articles)} articles from website")
        else:
            logger.warning("Website URL not provided. Skipping website scrape.")
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")

    # Create output directory if it doesn't exist
    output_dir = "output"
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"Created output directory: {output_dir}")
    except Exception as e:
        logger.error(f"Error creating output directory: {str(e)}")
        return

    # Save articles to JSON file
    output_file = os.path.join(output_dir, "articles.json")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_articles, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(all_articles)} articles to {output_file}")
    except Exception as e:
        logger.error(f"Error saving articles to JSON: {str(e)}")
        return

    # Print summary using logging
    logger.info("=" * 60)
    logger.info("FETCH SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total articles fetched: {len(all_articles)}")

    if all_articles:
        # Count articles by source
        source_counts: Dict[str, int] = {}
        for article in all_articles:
            source = article.get("source", "Unknown")
            source_counts[source] = source_counts.get(source, 0) + 1

        logger.info("Articles by source:")
        for source, count in sorted(source_counts.items()):
            logger.info(f"  - {source}: {count}")
    else:
        logger.warning("No articles were fetched from any source.")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
