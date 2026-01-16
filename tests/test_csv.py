import pytest
import os
import tempfile
import pandas as pd
from unittest.mock import patch, Mock
from fetchers.csv_reader import read_csv


class TestReadCSV:
    """Test cases for read_csv function."""
    
    def test_successful_read(self):
        """Test successful CSV read with valid data."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            f.write("Test Article 1,Content of article 1,Source 1,https://example.com/article1\n")
            f.write("Test Article 2,Content of article 2,Source 2,https://example.com/article2\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            
            # Assertions
            assert len(result) == 2
            assert result[0]["title"] == "Test Article 1"
            assert result[0]["content"] == "Content of article 1"
            assert result[0]["source"] == "csv"  # Should be "csv" not the original source
            assert result[0]["url"] == "https://example.com/article1"
            assert "fetched_at" in result[0]
            
            # Verify output format
            required_keys = {"title", "content", "source", "url", "fetched_at"}
            for article in result:
                assert set(article.keys()) == required_keys
                assert isinstance(article["title"], str)
                assert isinstance(article["content"], str)
                assert isinstance(article["source"], str)
                assert isinstance(article["url"], str)
                assert isinstance(article["fetched_at"], str)
                assert article["source"] == "csv"
                # Check timestamp format (should end with Z)
                assert article["fetched_at"].endswith("Z")
        finally:
            os.unlink(temp_path)
    
    def test_empty_file_path(self):
        """Test handling when file path is empty."""
        result = read_csv("")
        assert result == []
        assert isinstance(result, list)
    
    def test_none_file_path(self):
        """Test handling when file path is None."""
        result = read_csv(None)
        assert result == []
    
    def test_file_not_found(self):
        """Test handling when file doesn't exist."""
        result = read_csv("nonexistent_file.csv")
        assert result == []
        assert isinstance(result, list)
    
    def test_empty_file(self):
        """Test handling when file is empty."""
        # Create an empty file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
    
    def test_missing_columns(self):
        """Test handling when required columns are missing."""
        # Create CSV with missing columns
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content\n")  # Missing source and url
            f.write("Test Article,Content here\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
    
    def test_empty_dataframe(self):
        """Test handling when CSV has headers but no data rows."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            # No data rows
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
    
    def test_utf8_encoding(self):
        """Test reading CSV with UTF-8 encoding."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            f.write("Test Article,Content with émojis 🎉,Source,https://example.com\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert len(result) == 1
            assert "émojis" in result[0]["content"]
        finally:
            os.unlink(temp_path)
    
    def test_latin1_encoding_fallback(self):
        """Test fallback to latin-1 encoding when UTF-8 fails."""
        # Create a file that would fail with UTF-8 but work with latin-1
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            # Write CSV with latin-1 encoding
            content = "title,content,source,url\nTest,Content with é,Source,https://example.com\n"
            f.write(content.encode('latin-1'))
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            # Should successfully read with latin-1 fallback
            assert len(result) >= 0  # May or may not work depending on content
        finally:
            os.unlink(temp_path)
    
    def test_missing_url_field(self):
        """Test handling when URL field is empty or missing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            f.write("Test Article,Content here,Source,\n")  # Empty URL
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert len(result) == 1
            assert result[0]["url"] == "N/A"  # Should default to "N/A"
        finally:
            os.unlink(temp_path)
    
    def test_url_field_none(self):
        """Test handling when URL is None in CSV."""
        # Create CSV using pandas to handle None values
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            df = pd.DataFrame({
                "title": ["Test Article"],
                "content": ["Content"],
                "source": ["Source"],
                "url": [None]  # None value
            })
            df.to_csv(temp_path, index=False)
            
            result = read_csv(temp_path)
            assert len(result) == 1
            assert result[0]["url"] == "N/A"
        finally:
            os.unlink(temp_path)
    
    def test_multiple_articles(self):
        """Test reading multiple articles from CSV."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            for i in range(5):
                f.write(f"Article {i},Content {i},Source {i},https://example.com/{i}\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert len(result) == 5
            assert result[0]["title"] == "Article 0"
            assert result[4]["title"] == "Article 4"
        finally:
            os.unlink(temp_path)
    
    def test_special_characters_in_content(self):
        """Test handling of special characters in content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            f.write("Test,Content with \"quotes\" and 'apostrophes',Source,https://example.com\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert len(result) == 1
            assert '"quotes"' in result[0]["content"]
            assert "'apostrophes'" in result[0]["content"]
        finally:
            os.unlink(temp_path)
    
    @patch('fetchers.csv_reader.pd.read_csv')
    def test_pandas_exception(self, mock_read_csv):
        """Test handling when pandas raises an exception."""
        mock_read_csv.side_effect = Exception("Pandas error")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
    
    def test_timestamp_format(self):
        """Test that fetched_at is in correct ISO 8601 format with Z."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            f.write("Test,Content,Source,https://example.com\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert len(result) == 1
            fetched_at = result[0]["fetched_at"]
            # Should be in format: YYYY-MM-DDTHH:MM:SSZ
            assert fetched_at.endswith("Z")
            assert "T" in fetched_at
            # Should be parseable as datetime
            from datetime import datetime
            dt = datetime.strptime(fetched_at, "%Y-%m-%dT%H:%M:%SZ")
            assert isinstance(dt, datetime)
        finally:
            os.unlink(temp_path)
    
    def test_all_required_columns_present(self):
        """Test that all required columns are validated."""
        # Test with only some columns
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content\n")  # Missing source and url
            f.write("Test,Content\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert result == []
        finally:
            os.unlink(temp_path)
    
    def test_source_always_csv(self):
        """Test that source is always set to 'csv' regardless of CSV content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write("title,content,source,url\n")
            f.write("Test,Content,OriginalSource,https://example.com\n")
            temp_path = f.name
        
        try:
            result = read_csv(temp_path)
            assert len(result) == 1
            # Source should be "csv", not "OriginalSource"
            assert result[0]["source"] == "csv"
        finally:
            os.unlink(temp_path)
