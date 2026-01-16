import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required columns in the CSV file
REQUIRED_COLUMNS = ["title", "content", "source", "url"]


def read_csv(file_path: str) -> List[Dict[str, str]]:
    """
    Reads a CSV file with article data and returns formatted list of dictionaries.
    
    Args:
        file_path: Path to the CSV file to read
        
    Returns:
        List of dictionaries with keys: title, content, source, url, fetched_at
        Returns empty list on failure
    """
    if not file_path:
        logger.error("File path is required but not provided")
        return []
    
    # Check if file exists
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return []
    
    # Check if file is empty
    if os.path.getsize(file_path) == 0:
        logger.error(f"File is empty: {file_path}")
        return []
    
    # Try reading with different encodings
    encodings = ["utf-8", "latin-1"]
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"Successfully read CSV file with {encoding} encoding")
            break
        except UnicodeDecodeError as e:
            logger.warning(f"Failed to read with {encoding} encoding: {str(e)}")
            continue
        except Exception as e:
            logger.error(f"Error reading CSV file with {encoding} encoding: {str(e)}")
            return []
    
    if df is None:
        logger.error(f"Failed to read CSV file with any supported encoding (tried: {', '.join(encodings)})")
        return []
    
    # Check if DataFrame is empty
    if df.empty:
        logger.error("CSV file contains no data rows")
        return []
    
    # Validate required columns exist
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        logger.error(f"Missing required columns in CSV: {', '.join(missing_columns)}")
        logger.error(f"Available columns: {', '.join(df.columns.tolist())}")
        return []
    
    # Format articles according to required structure
    formatted_articles = []
    fetched_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    try:
        for _, row in df.iterrows():
            formatted_article = {
                "title": str(row.get("title", "")),
                "content": str(row.get("content", "")),
                "source": "csv",  # Fixed source value as per assignment
                "url": str(row.get("url", "")) or "N/A",  # Use "N/A" if URL is missing
                "fetched_at": fetched_at
            }
            formatted_articles.append(formatted_article)
        
        logger.info(f"Successfully read {len(formatted_articles)} articles from CSV file: {file_path}")
        return formatted_articles
        
    except Exception as e:
        logger.error(f"Error processing CSV data: {str(e)}")
        return []
