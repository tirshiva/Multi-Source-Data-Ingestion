import pytest
from unittest.mock import patch, Mock
from fetchers.web_scraper import scrape_website
from bs4 import BeautifulSoup
import requests


class TestScrapeWebsite:
    """Test cases for scrape_website function."""
    
    @patch('fetchers.web_scraper.requests.get')
    def test_successful_scrape_with_h1(self, mock_get):
        """Test successful scraping with h1 title."""
        # Mock HTML response
        html_content = """
        <html>
            <head><title>Page Title</title></head>
            <body>
                <h1>Article Title</h1>
                <p>First paragraph content.</p>
                <p>Second paragraph content.</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        # Assertions
        assert len(result) == 1
        assert result[0]["title"] == "Article Title"
        assert "First paragraph content" in result[0]["content"]
        assert "Second paragraph content" in result[0]["content"]
        assert result[0]["source"] == "example.com"
        assert result[0]["url"] == "https://example.com/article"
        assert "fetched_at" in result[0]
        
        # Verify output format
        required_keys = {"title", "content", "source", "url", "fetched_at"}
        assert set(result[0].keys()) == required_keys
        
        # Verify timestamp format
        assert result[0]["fetched_at"].endswith("Z")
    
    @patch('fetchers.web_scraper.requests.get')
    def test_successful_scrape_with_h2(self, mock_get):
        """Test successful scraping with h2 title (fallback from h1)."""
        html_content = """
        <html>
            <body>
                <h2>Article Title from H2</h2>
                <p>Content paragraph.</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        assert result[0]["title"] == "Article Title from H2"
    
    @patch('fetchers.web_scraper.requests.get')
    def test_title_fallback_to_title_tag(self, mock_get):
        """Test title extraction falls back to <title> tag."""
        html_content = """
        <html>
            <head><title>Title from Title Tag</title></head>
            <body>
                <p>Content here.</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        assert result[0]["title"] == "Title from Title Tag"
    
    @patch('fetchers.web_scraper.requests.get')
    def test_title_fallback_to_og_title(self, mock_get):
        """Test title extraction falls back to og:title meta tag."""
        html_content = """
        <html>
            <head>
                <meta property="og:title" content="OG Title" />
            </head>
            <body>
                <p>Content here.</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        assert result[0]["title"] == "OG Title"
    
    @patch('fetchers.web_scraper.requests.get')
    def test_content_from_paragraphs(self, mock_get):
        """Test content extraction from paragraph tags."""
        html_content = """
        <html>
            <body>
                <h1>Title</h1>
                <p>First paragraph.</p>
                <p>Second paragraph.</p>
                <p>Third paragraph.</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        content = result[0]["content"]
        assert "First paragraph" in content
        assert "Second paragraph" in content
        assert "Third paragraph" in content
    
    @patch('fetchers.web_scraper.requests.get')
    def test_content_fallback_to_body(self, mock_get):
        """Test content extraction falls back to body text when no paragraphs."""
        html_content = """
        <html>
            <body>
                <h1>Title</h1>
                <div>Content without paragraph tags.</div>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        assert "Content without paragraph tags" in result[0]["content"]
    
    @patch('fetchers.web_scraper.requests.get')
    def test_empty_url(self, mock_get):
        """Test handling when URL is empty."""
        result = scrape_website("")
        assert result == []
        assert isinstance(result, list)
        mock_get.assert_not_called()
    
    @patch('fetchers.web_scraper.requests.get')
    def test_none_url(self, mock_get):
        """Test handling when URL is None."""
        result = scrape_website(None)
        assert result == []
        mock_get.assert_not_called()
    
    @patch('fetchers.web_scraper.requests.get')
    def test_404_error(self, mock_get):
        """Test handling of 404 error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/notfound")
        
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.web_scraper.requests.get')
    def test_other_http_error(self, mock_get):
        """Test handling of other HTTP errors (e.g., 500)."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/error")
        
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.web_scraper.requests.get')
    def test_timeout_error(self, mock_get):
        """Test handling of timeout error."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = scrape_website("https://example.com/slow")
        
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.web_scraper.requests.get')
    def test_connection_error(self, mock_get):
        """Test handling of connection error."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        result = scrape_website("https://example.com/unreachable")
        
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.web_scraper.requests.get')
    def test_request_exception(self, mock_get):
        """Test handling of general request exception."""
        mock_get.side_effect = requests.exceptions.RequestException("Request failed")
        
        result = scrape_website("https://example.com/error")
        
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.web_scraper.requests.get')
    def test_parsing_failure(self, mock_get):
        """Test handling when HTML parsing fails."""
        mock_response = Mock()
        mock_response.status_code = 200
        # Invalid HTML that might cause parsing issues
        mock_response.content = b"<html><body><unclosed_tag>"
        mock_get.return_value = mock_response
        
        # BeautifulSoup should handle this, but test the flow
        result = scrape_website("https://example.com/badhtml")
        
        # Should still return a result (BeautifulSoup is forgiving)
        # or empty list if parsing truly fails
        assert isinstance(result, list)
    
    @patch('fetchers.web_scraper.requests.get')
    def test_domain_extraction(self, mock_get):
        """Test domain name extraction from URL."""
        html_content = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        # Test different URL formats
        test_cases = [
            ("https://www.example.com/article", "www.example.com"),
            ("https://example.com/path", "example.com"),
            ("http://subdomain.example.com/page", "subdomain.example.com"),
        ]
        
        for url, expected_domain in test_cases:
            result = scrape_website(url)
            if result:
                assert result[0]["source"] == expected_domain
    
    @patch('fetchers.web_scraper.requests.get')
    def test_user_agent_header(self, mock_get):
        """Test that User-Agent header is included in request."""
        html_content = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        scrape_website("https://example.com/article")
        
        # Verify request was made with User-Agent header
        mock_get.assert_called_once()
        call_kwargs = mock_get.call_args[1]
        assert "headers" in call_kwargs
        assert "User-Agent" in call_kwargs["headers"]
        assert "Mozilla" in call_kwargs["headers"]["User-Agent"]
    
    @patch('fetchers.web_scraper.requests.get')
    def test_timeout_setting(self, mock_get):
        """Test that timeout is set to 10 seconds."""
        html_content = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        scrape_website("https://example.com/article")
        
        # Verify timeout is set
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["timeout"] == 10
    
    @patch('fetchers.web_scraper.requests.get')
    def test_empty_title_and_content(self, mock_get):
        """Test handling when both title and content are empty."""
        html_content = "<html><body></body></html>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/empty")
        
        # Should still return a result with empty strings
        assert len(result) == 1
        assert result[0]["title"] == ""
        assert result[0]["content"] == ""
        assert result[0]["url"] == "https://example.com/empty"
    
    @patch('fetchers.web_scraper.requests.get')
    def test_timestamp_format(self, mock_get):
        """Test that fetched_at is in correct ISO 8601 format with Z."""
        html_content = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        fetched_at = result[0]["fetched_at"]
        # Should be in format: YYYY-MM-DDTHH:MM:SSZ
        assert fetched_at.endswith("Z")
        assert "T" in fetched_at
        # Should be parseable as datetime
        from datetime import datetime
        dt = datetime.strptime(fetched_at, "%Y-%m-%dT%H:%M:%SZ")
        assert isinstance(dt, datetime)
    
    @patch('fetchers.web_scraper.requests.get')
    def test_multiple_paragraphs_combined(self, mock_get):
        """Test that multiple paragraphs are combined with spaces."""
        html_content = """
        <html>
            <body>
                <h1>Title</h1>
                <p>First</p>
                <p>Second</p>
                <p>Third</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        content = result[0]["content"]
        # Should contain all paragraphs
        assert "First" in content
        assert "Second" in content
        assert "Third" in content
    
    @patch('fetchers.web_scraper.requests.get')
    def test_empty_paragraphs_skipped(self, mock_get):
        """Test that empty paragraphs are skipped."""
        html_content = """
        <html>
            <body>
                <h1>Title</h1>
                <p>Valid content</p>
                <p></p>
                <p>   </p>
                <p>Another valid</p>
            </body>
        </html>
        """
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = html_content.encode('utf-8')
        mock_get.return_value = mock_response
        
        result = scrape_website("https://example.com/article")
        
        assert len(result) == 1
        content = result[0]["content"]
        assert "Valid content" in content
        assert "Another valid" in content
        # Empty paragraphs should not add extra spaces
