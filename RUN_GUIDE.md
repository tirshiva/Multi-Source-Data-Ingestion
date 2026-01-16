# Project Run Guide

This guide will help you run the news article fetcher project and verify it's working correctly.

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Internet connection** (for NewsAPI and web scraping)

## Step 1: Install Dependencies

First, install all required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - for HTTP requests
- `pandas` - for CSV reading
- `beautifulsoup4` - for web scraping
- `python-dotenv` - for environment variables (optional)
- `pytest` - for running tests

## Step 2: Set Up Environment Variables (Optional)

The project uses environment variables for configuration. You can set them in two ways:

### Option A: Export in Terminal (Linux/Mac)

```bash
export NEWSAPI_KEY="your_newsapi_key_here"
export NEWSAPI_QUERY="technology"
export CSV_FILE_PATH="data/articles.csv"
export WEBSITE_URL="https://example.com/article"
```

### Option B: Create a `.env` file (requires python-dotenv)

Create a `.env` file in the project root:

```bash
NEWSAPI_KEY=your_newsapi_key_here
NEWSAPI_QUERY=technology
CSV_FILE_PATH=data/articles.csv
WEBSITE_URL=https://example.com/article
```

**Note:** If you don't set these variables, the script will:
- Skip NewsAPI if no key is provided
- Look for CSV at `data/articles.csv` (default)
- Skip web scraping if no URL is provided

## Step 3: Get a NewsAPI Key (Optional)

If you want to test NewsAPI:

1. Go to https://newsapi.org/
2. Sign up for a free account
3. Get your API key from the dashboard
4. Set it as `NEWSAPI_KEY` environment variable

**Free tier limits:** 100 requests per day

## Step 4: Prepare Test Data

### CSV File

A sample CSV file is already created at `data/articles.csv`. It contains:
- Required columns: `title`, `content`, `source`, `url`
- 3 sample articles

You can modify this file or create your own CSV with the same column structure.

**CSV Format:**
```csv
title,content,source,url
Article Title,Article content here,Source Name,https://example.com
```

### Web Scraping URL

You can test web scraping with any news article URL. Some examples:
- `https://www.bbc.com/news/technology`
- `https://techcrunch.com/`
- Any news article page

## Step 5: Run the Project

### Basic Run

Simply execute:

```bash
python main.py
```

### Expected Output

You should see logging output like:

```
2025-01-15 10:30:00,123 - __main__ - INFO - Starting NewsAPI fetch...
2025-01-15 10:30:01,456 - fetchers.newsapi - INFO - Successfully fetched 10 articles for query: technology
2025-01-15 10:30:01,457 - __main__ - INFO - Fetched 10 articles from NewsAPI
2025-01-15 10:30:01,458 - __main__ - INFO - Starting CSV read...
2025-01-15 10:30:01,500 - fetchers.csv_reader - INFO - Successfully read CSV file with utf-8 encoding
2025-01-15 10:30:01,501 - __main__ - INFO - Read 3 articles from CSV
2025-01-15 10:30:01,502 - __main__ - INFO - Starting website scrape...
2025-01-15 10:30:02,100 - fetchers.web_scraper - INFO - Successfully scraped article from URL: https://example.com
2025-01-15 10:30:02,101 - __main__ - INFO - Scraped 1 articles from website
2025-01-15 10:30:02,102 - __main__ - INFO - Saved 14 articles to output/articles.json
2025-01-15 10:30:02,103 - __main__ - INFO - ============================================================
2025-01-15 10:30:02,104 - __main__ - INFO - FETCH SUMMARY
2025-01-15 10:30:02,105 - __main__ - INFO - ============================================================
2025-01-15 10:30:02,106 - __main__ - INFO - Total articles fetched: 14
2025-01-15 10:30:02,107 - __main__ - INFO - Articles by source:
2025-01-15 10:30:02,108 - __main__ - INFO -   - newsapi: 10
2025-01-15 10:30:02,109 - __main__ - INFO -   - csv: 3
2025-01-15 10:30:02,110 - __main__ - INFO -   - example.com: 1
```

## Step 6: Verify Output

Check the generated JSON file:

```bash
cat output/articles.json
```

Or open it in a text editor. The output should match this format:

```json
[
  {
    "title": "India launches...",
    "content": "Full text here",
    "source": "newsapi",
    "url": "https://...",
    "fetched_at": "2025-01-15T10:30:00Z"
  },
  {
    "title": "Government announces...",
    "content": "Full text here",
    "source": "csv",
    "url": "N/A",
    "fetched_at": "2025-01-15T10:30:00Z"
  }
]
```

### Output Format Verification

Each article should have:
- ✅ `title` - string
- ✅ `content` - string
- ✅ `source` - string ("newsapi", "csv", or domain name)
- ✅ `url` - string (or "N/A" if missing)
- ✅ `fetched_at` - ISO 8601 timestamp with 'Z' suffix (UTC)

## Step 7: Test Individual Components

### Test NewsAPI Only

```bash
export NEWSAPI_KEY="your_key"
export NEWSAPI_QUERY="technology"
python -c "from fetchers.newsapi import fetch_newsapi; import os; print(fetch_newsapi(os.getenv('NEWSAPI_KEY'), os.getenv('NEWSAPI_QUERY')))"
```

### Test CSV Reader Only

```bash
python -c "from fetchers.csv_reader import read_csv; print(read_csv('data/articles.csv'))"
```

### Test Web Scraper Only

```bash
python -c "from fetchers.web_scraper import scrape_website; print(scrape_website('https://example.com'))"
```

## Step 8: Run Tests

Run the test suite:

```bash
pytest tests/
```

Or run specific test files:

```bash
pytest tests/test_newsapi.py -v
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fetchers'"

**Solution:** Make sure you're running from the project root directory:

```bash
cd /home/shivanshu-tiwari/Documents/coding_assignment
python main.py
```

### Issue: "NewsAPI key not provided"

**Solution:** This is expected if you haven't set the API key. The script will skip NewsAPI and continue with other sources. To fix:

```bash
export NEWSAPI_KEY="your_key_here"
```

### Issue: "CSV file not found"

**Solution:** Check if the file exists:

```bash
ls -la data/articles.csv
```

If it doesn't exist, create it or update the `CSV_FILE_PATH` environment variable.

### Issue: "Rate limit exceeded (429)"

**Solution:** NewsAPI free tier has limits. Wait a few minutes or upgrade your plan.

### Issue: "Authentication failed (401)"

**Solution:** Your NewsAPI key is invalid. Check it at https://newsapi.org/account

### Issue: Web scraping returns empty content

**Solution:** Some websites block scrapers. Try a different URL or check if the site requires JavaScript (this scraper doesn't handle JS).

### Issue: Encoding errors with CSV

**Solution:** The script tries UTF-8 first, then Latin-1. If both fail, check your CSV file encoding. You can convert it:

```bash
iconv -f <original_encoding> -t utf-8 input.csv > output.csv
```

## Testing Different Scenarios

### Test with Only CSV

```bash
unset NEWSAPI_KEY
unset WEBSITE_URL
export CSV_FILE_PATH="data/articles.csv"
python main.py
```

### Test with Only NewsAPI

```bash
export NEWSAPI_KEY="your_key"
export NEWSAPI_QUERY="technology"
unset CSV_FILE_PATH
unset WEBSITE_URL
python main.py
```

### Test with Only Web Scraping

```bash
unset NEWSAPI_KEY
unset CSV_FILE_PATH
export WEBSITE_URL="https://example.com/article"
python main.py
```

## Expected Behavior

- ✅ Script continues even if one source fails
- ✅ Creates `output/` directory if missing
- ✅ Logs all operations (INFO, WARNING, ERROR levels)
- ✅ Returns empty list `[]` on errors (doesn't crash)
- ✅ Combines all successful fetches
- ✅ Saves to `output/articles.json` with proper formatting

## Verification Checklist

After running, verify:

- [ ] `output/articles.json` file exists
- [ ] JSON is valid (can be parsed)
- [ ] All articles have required fields: title, content, source, url, fetched_at
- [ ] Source values are correct: "newsapi", "csv", or domain name
- [ ] Timestamps are in ISO 8601 format with 'Z' suffix
- [ ] Missing URLs show as "N/A"
- [ ] Log output shows summary with article counts by source

## Next Steps

Once everything is working:

1. **Customize sources:** Modify environment variables to use your preferred sources
2. **Add more CSV files:** Create additional CSV files with different articles
3. **Test error handling:** Try invalid API keys, missing files, etc.
4. **Run tests:** Execute `pytest tests/` to verify all components
5. **Review output:** Check `output/articles.json` for data quality

## Quick Start (Minimal Setup)

If you just want to test quickly without NewsAPI:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with just CSV (sample file already exists)
python main.py

# 3. Check output
cat output/articles.json
```

This will use the sample CSV file at `data/articles.csv` and skip NewsAPI/web scraping if not configured.
