# Quick Start Guide

## 🚀 Run the Project in 3 Steps

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Project
```bash
python main.py
```

### Step 3: Check Output
```bash
cat output/articles.json
```

That's it! The project will:
- ✅ Read articles from `data/articles.csv` (sample file included)
- ⚠️ Skip NewsAPI (if no API key set)
- ⚠️ Skip web scraping (if no URL set)

## 📋 Full Setup (Optional)

### To Test NewsAPI:
```bash
export NEWSAPI_KEY="your_api_key_here"
export NEWSAPI_QUERY="technology"
python main.py
```

Get a free API key at: https://newsapi.org/

### To Test Web Scraping:
```bash
export WEBSITE_URL="https://example.com/article"
python main.py
```

## ✅ Verify It's Working

Run the quick test:
```bash
python quick_test.py
```

Or manually check:
```bash
# Check if output file exists and is valid JSON
python -c "import json; print(json.load(open('output/articles.json')))"
```

## 📝 Expected Output Format

The `output/articles.json` file should contain:

```json
[
  {
    "title": "Article Title",
    "content": "Article content here...",
    "source": "csv",
    "url": "N/A",
    "fetched_at": "2025-01-15T10:30:00Z"
  }
]
```

**Key points:**
- `source` should be: `"newsapi"`, `"csv"`, or domain name
- `url` should be a URL or `"N/A"` if missing
- `fetched_at` should be ISO 8601 format with `Z` suffix (UTC)

## 🐛 Troubleshooting

**"ModuleNotFoundError"** → Make sure you're in the project root directory

**"CSV file not found"** → Check that `data/articles.csv` exists

**"No articles fetched"** → Check the logs for error messages

For more details, see `RUN_GUIDE.md`
