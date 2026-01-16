import pytest
import os
import json
import tempfile
import shutil
from unittest.mock import patch, Mock, call
from main import main


class TestMain:
    """Test cases for main function."""
    
    def setup_method(self):
        """Set up test fixtures before each test."""
        # Create a temporary directory for output
        self.test_output_dir = tempfile.mkdtemp()
        self.original_output_dir = "output"
    
    def teardown_method(self):
        """Clean up after each test."""
        # Remove temporary output directory if it exists
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        # Clean up any test output directories
        if os.path.exists("output"):
            # Only remove if it's empty or contains test files
            try:
                shutil.rmtree("output")
            except:
                pass
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'NEWSAPI_QUERY': 'technology',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_main_all_sources_success(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test main function with all sources providing data."""
        # Mock all fetchers to return articles
        mock_fetch_newsapi.return_value = [
            {"title": "NewsAPI Article", "content": "Content 1", "source": "newsapi", 
             "url": "https://example.com/1", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_read_csv.return_value = [
            {"title": "CSV Article", "content": "Content 2", "source": "csv", 
             "url": "N/A", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_scrape_website.return_value = [
            {"title": "Scraped Article", "content": "Content 3", "source": "example.com", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        # Mock os.path.exists for CSV file
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            main()
        
        # Verify all fetchers were called
        mock_fetch_newsapi.assert_called_once_with('test_key', 'technology')
        mock_read_csv.assert_called_once_with('test.csv')
        mock_scrape_website.assert_called_once_with('https://example.com')
        
        # Verify output file was created
        assert os.path.exists("output/articles.json")
        
        # Verify JSON content
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        assert len(articles) == 3
        assert articles[0]["title"] == "NewsAPI Article"
        assert articles[1]["title"] == "CSV Article"
        assert articles[2]["title"] == "Scraped Article"
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {}, clear=True)
    def test_main_no_env_variables(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test main function when no environment variables are set."""
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = False  # CSV file doesn't exist
            main()
        
        # NewsAPI should not be called (no API key)
        mock_fetch_newsapi.assert_not_called()
        
        # CSV should not be called (file doesn't exist)
        mock_read_csv.assert_not_called()
        
        # Web scraper should not be called (no URL)
        mock_scrape_website.assert_not_called()
        
        # Output file should still be created (empty list)
        assert os.path.exists("output/articles.json")
        
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        assert articles == []
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {'NEWSAPI_KEY': 'test_key'})
    def test_main_only_newsapi(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test main function with only NewsAPI configured."""
        mock_fetch_newsapi.return_value = [
            {"title": "NewsAPI Article", "content": "Content", "source": "newsapi", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = False  # CSV file doesn't exist
            main()
        
        mock_fetch_newsapi.assert_called_once()
        mock_read_csv.assert_not_called()
        mock_scrape_website.assert_not_called()
        
        # Verify output
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        assert len(articles) == 1
        assert articles[0]["title"] == "NewsAPI Article"
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {'CSV_FILE_PATH': 'test.csv'})
    def test_main_only_csv(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test main function with only CSV configured."""
        mock_read_csv.return_value = [
            {"title": "CSV Article", "content": "Content", "source": "csv", 
             "url": "N/A", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            main()
        
        mock_fetch_newsapi.assert_not_called()
        mock_read_csv.assert_called_once_with('test.csv')
        mock_scrape_website.assert_not_called()
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {'WEBSITE_URL': 'https://example.com'})
    def test_main_only_web_scraper(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test main function with only web scraper configured."""
        mock_scrape_website.return_value = [
            {"title": "Scraped Article", "content": "Content", "source": "example.com", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = False  # CSV file doesn't exist
            main()
        
        mock_fetch_newsapi.assert_not_called()
        mock_read_csv.assert_not_called()
        mock_scrape_website.assert_called_once_with('https://example.com')
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_main_newsapi_error_continues(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that main continues when NewsAPI fails."""
        mock_fetch_newsapi.side_effect = Exception("NewsAPI error")
        mock_read_csv.return_value = [
            {"title": "CSV Article", "content": "Content", "source": "csv", 
             "url": "N/A", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_scrape_website.return_value = [
            {"title": "Scraped Article", "content": "Content", "source": "example.com", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        with patch('main.os.path.exists') as mock_exists:
            # First call: CSV file exists, Second call: output directory exists
            mock_exists.side_effect = [True, True]
            main()
        
        # Other fetchers should still be called
        mock_read_csv.assert_called_once()
        mock_scrape_website.assert_called_once()
        
        # Output should contain articles from other sources
        assert os.path.exists("output/articles.json")
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        assert len(articles) == 2
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_main_csv_error_continues(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that main continues when CSV read fails."""
        mock_fetch_newsapi.return_value = [
            {"title": "NewsAPI Article", "content": "Content", "source": "newsapi", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_read_csv.side_effect = Exception("CSV error")
        mock_scrape_website.return_value = [
            {"title": "Scraped Article", "content": "Content", "source": "example.com", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            main()
        
        # Other fetchers should still be called
        mock_fetch_newsapi.assert_called_once()
        mock_scrape_website.assert_called_once()
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_main_web_scraper_error_continues(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that main continues when web scraper fails."""
        mock_fetch_newsapi.return_value = [
            {"title": "NewsAPI Article", "content": "Content", "source": "newsapi", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_read_csv.return_value = [
            {"title": "CSV Article", "content": "Content", "source": "csv", 
             "url": "N/A", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_scrape_website.side_effect = Exception("Scraper error")
        
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            main()
        
        # Other fetchers should still be called
        mock_fetch_newsapi.assert_called_once()
        mock_read_csv.assert_called_once()
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_output_directory_creation(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that output directory is created if it doesn't exist."""
        # Remove output directory if it exists
        if os.path.exists("output"):
            shutil.rmtree("output")
        
        mock_fetch_newsapi.return_value = []
        mock_read_csv.return_value = []
        mock_scrape_website.return_value = []
        
        with patch('main.os.path.exists') as mock_exists:
            # First call for CSV file check, second for output directory
            mock_exists.side_effect = [True, False]
            with patch('main.os.makedirs') as mock_makedirs:
                main()
                # Verify makedirs was called
                mock_makedirs.assert_called_once_with("output")
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_json_file_creation(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that JSON file is created with correct format."""
        articles = [
            {"title": "Article 1", "content": "Content 1", "source": "newsapi", 
             "url": "https://example.com/1", "fetched_at": "2025-01-15T10:00:00Z"},
            {"title": "Article 2", "content": "Content 2", "source": "csv", 
             "url": "N/A", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        mock_fetch_newsapi.return_value = [articles[0]]
        mock_read_csv.return_value = [articles[1]]
        mock_scrape_website.return_value = []
        
        with patch('main.os.path.exists') as mock_exists:
            # First call: CSV file exists, Second call: output directory exists
            mock_exists.side_effect = [True, True]
            main()
        
        # Verify file exists and has correct content
        assert os.path.exists("output/articles.json")
        
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            saved_articles = json.load(f)
        
        assert len(saved_articles) == 2
        assert saved_articles[0]["title"] == "Article 1"
        assert saved_articles[1]["title"] == "Article 2"
        # Verify JSON is properly formatted (indented)
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            content = f.read()
            assert content.startswith('[\n')  # Should be indented
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_summary_counting_by_source(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that summary correctly counts articles by source."""
        mock_fetch_newsapi.return_value = [
            {"title": "Article 1", "content": "Content", "source": "newsapi", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"},
            {"title": "Article 2", "content": "Content", "source": "newsapi", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_read_csv.return_value = [
            {"title": "Article 3", "content": "Content", "source": "csv", 
             "url": "N/A", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        mock_scrape_website.return_value = [
            {"title": "Article 4", "content": "Content", "source": "example.com", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        with patch('main.os.path.exists') as mock_exists:
            # First call: CSV file exists, Second call: output directory exists
            mock_exists.side_effect = [True, True]
            main()
        
        # Verify all articles are saved
        assert os.path.exists("output/articles.json")
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        assert len(articles) == 4
        
        # Count by source
        source_counts = {}
        for article in articles:
            source = article["source"]
            source_counts[source] = source_counts.get(source, 0) + 1
        
        assert source_counts["newsapi"] == 2
        assert source_counts["csv"] == 1
        assert source_counts["example.com"] == 1
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {}, clear=True)
    def test_empty_articles_summary(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test summary when no articles are fetched."""
        main()
        
        # Verify empty list is saved
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        assert articles == []
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch('main.os.makedirs')
    @patch.dict(os.environ, {}, clear=True)
    def test_output_directory_creation_error(self, mock_makedirs, mock_fetch_newsapi, 
                                             mock_read_csv, mock_scrape_website):
        """Test that main returns early if output directory creation fails."""
        # Remove output if exists
        if os.path.exists("output"):
            shutil.rmtree("output")
        
        mock_makedirs.side_effect = PermissionError("Permission denied")
        
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            main()
        
        # Should return early, so JSON file should not be created
        assert not os.path.exists("output/articles.json")
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch('main.open', side_effect=IOError("Disk full"))
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key'
    })
    def test_json_save_error(self, mock_open, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that main handles JSON save errors gracefully."""
        mock_fetch_newsapi.return_value = [
            {"title": "Article", "content": "Content", "source": "newsapi", 
             "url": "https://example.com", "fetched_at": "2025-01-15T10:00:00Z"}
        ]
        
        main()
        
        # Function should complete without crashing
        # (The error is logged but doesn't stop execution)
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'NEWSAPI_QUERY': 'custom_query'
    })
    def test_custom_newsapi_query(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that custom NEWSAPI_QUERY is used."""
        mock_fetch_newsapi.return_value = []
        
        main()
        
        # Verify query parameter is passed
        mock_fetch_newsapi.assert_called_once_with('test_key', 'custom_query')
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'custom_path.csv'
    })
    def test_custom_csv_path(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that custom CSV_FILE_PATH is used."""
        mock_read_csv.return_value = []
        
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = True
            main()
        
        # Verify custom path is used
        mock_read_csv.assert_called_once_with('custom_path.csv')
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'CSV_FILE_PATH': 'nonexistent.csv'
    })
    def test_csv_file_not_found(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test that CSV read is skipped when file doesn't exist."""
        with patch('main.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            main()
        
        # CSV should not be called
        mock_read_csv.assert_not_called()
    
    @patch('main.scrape_website')
    @patch('main.read_csv')
    @patch('main.fetch_newsapi')
    @patch.dict(os.environ, {
        'NEWSAPI_KEY': 'test_key',
        'CSV_FILE_PATH': 'test.csv',
        'WEBSITE_URL': 'https://example.com'
    })
    def test_all_fetchers_return_empty(self, mock_fetch_newsapi, mock_read_csv, mock_scrape_website):
        """Test main when all fetchers return empty lists."""
        mock_fetch_newsapi.return_value = []
        mock_read_csv.return_value = []
        mock_scrape_website.return_value = []
        
        with patch('main.os.path.exists') as mock_exists:
            # First call: CSV file exists, Second call: output directory exists
            mock_exists.side_effect = [True, True]
            main()
        
        # All fetchers should be called
        mock_fetch_newsapi.assert_called_once()
        mock_read_csv.assert_called_once()
        mock_scrape_website.assert_called_once()
        
        # Output should be empty list
        assert os.path.exists("output/articles.json")
        with open("output/articles.json", 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        assert articles == []
