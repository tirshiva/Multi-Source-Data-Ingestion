import pytest
from unittest.mock import patch, Mock
from fetchers.newsapi import fetch_newsapi


class TestFetchNewsAPI:
    """Test cases for fetch_newsapi function."""
    
    @patch('fetchers.newsapi.requests.get')
    def test_successful_fetch(self, mock_get):
        """Test successful API fetch with valid response."""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 2,
            "articles": [
                {
                    "title": "Test Article 1",
                    "content": "This is the content of article 1",
                    "description": "Description of article 1",
                    "source": {"name": "Test Source 1"},
                    "url": "https://example.com/article1"
                },
                {
                    "title": "Test Article 2",
                    "content": None,
                    "description": "Description of article 2",
                    "source": {"name": "Test Source 2"},
                    "url": "https://example.com/article2"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Assertions
        assert len(result) == 2
        assert result[0]["title"] == "Test Article 1"
        assert result[0]["content"] == "This is the content of article 1"
        assert result[0]["source"] == "Test Source 1"
        assert result[0]["url"] == "https://example.com/article1"
        assert "fetched_at" in result[0]
        
        # Second article should use description when content is None
        assert result[1]["title"] == "Test Article 2"
        assert result[1]["content"] == "Description of article 2"
        assert result[1]["source"] == "Test Source 2"
        
        # Verify output format
        required_keys = {"title", "content", "source", "url", "fetched_at"}
        for article in result:
            assert set(article.keys()) == required_keys
            assert isinstance(article["title"], str)
            assert isinstance(article["content"], str)
            assert isinstance(article["source"], str)
            assert isinstance(article["url"], str)
            assert isinstance(article["fetched_at"], str)
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://newsapi.org/v2/everything"
        assert call_args[1]["params"]["q"] == "technology"
        assert call_args[1]["params"]["apiKey"] == "test_api_key"
        assert call_args[1]["params"]["pageSize"] == 10
        assert call_args[1]["timeout"] == 5
    
    @patch('fetchers.newsapi.requests.get')
    def test_timeout_error(self, mock_get):
        """Test handling of timeout error."""
        import requests
        
        # Mock timeout exception
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return empty list
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_rate_limit_429(self, mock_get):
        """Test handling of rate limit error (429)."""
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return empty list
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_auth_error_401(self, mock_get):
        """Test handling of authentication error (401)."""
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("invalid_api_key", "technology")
        
        # Should return empty list
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_other_http_error(self, mock_get):
        """Test handling of other HTTP errors."""
        # Mock 500 response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return empty list
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_api_status_not_ok(self, mock_get):
        """Test handling when API returns status != 'ok'."""
        # Mock response with status != 'ok'
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "error",
            "message": "Invalid query"
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return empty list
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_empty_articles_list(self, mock_get):
        """Test handling when API returns empty articles list."""
        # Mock response with empty articles
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 0,
            "articles": []
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return empty list
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_more_than_10_articles(self, mock_get):
        """Test that only top 10 articles are returned."""
        # Mock response with 15 articles
        articles = [
            {
                "title": f"Article {i}",
                "content": f"Content {i}",
                "description": f"Description {i}",
                "source": {"name": f"Source {i}"},
                "url": f"https://example.com/article{i}"
            }
            for i in range(15)
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 15,
            "articles": articles
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return only 10 articles
        assert len(result) == 10
        assert result[0]["title"] == "Article 0"
        assert result[9]["title"] == "Article 9"
    
    def test_empty_api_key(self):
        """Test handling when API key is empty."""
        result = fetch_newsapi("", "technology")
        assert result == []
    
    def test_empty_query(self):
        """Test handling when query is empty."""
        result = fetch_newsapi("test_api_key", "")
        assert result == []
    
    @patch('fetchers.newsapi.requests.get')
    def test_request_exception(self, mock_get):
        """Test handling of general request exception."""
        import requests
        
        # Mock request exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return empty list
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_missing_keys_in_response(self, mock_get):
        """Test handling when response is missing expected keys."""
        # Mock response with missing keys
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok"
            # Missing "articles" key
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should return empty list (articles key missing)
        assert result == []
        assert isinstance(result, list)
    
    @patch('fetchers.newsapi.requests.get')
    def test_article_missing_fields(self, mock_get):
        """Test handling when articles have missing fields."""
        # Mock response with articles missing some fields
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "ok",
            "articles": [
                {
                    "title": "Article with missing fields",
                    # Missing content, description, source, url
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Call the function
        result = fetch_newsapi("test_api_key", "technology")
        
        # Should still return article with empty strings for missing fields
        assert len(result) == 1
        assert result[0]["title"] == "Article with missing fields"
        assert result[0]["content"] == ""
        assert result[0]["source"] == ""
        assert result[0]["url"] == ""
        assert "fetched_at" in result[0]
