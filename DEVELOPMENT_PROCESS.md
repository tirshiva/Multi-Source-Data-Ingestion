# Development Process Documentation

## Problem Breakdown

When I first looked at this assignment, I needed to build a system that fetches news articles from three different sources and normalizes them into a consistent format. Here's how I broke it down:

1. **Three data sources to handle:**
   - NewsAPI (REST API with JSON responses)
   - CSV files (local file reading)
   - Web scraping (HTML parsing)

2. **Common requirements across all sources:**
   - Standardized output format: `{title, content, source, url, fetched_at}`
   - Error handling (timeouts, auth errors, file errors, etc.)
   - Logging instead of print statements
   - Return empty list on failure

3. **Main orchestration:**
   - Combine results from all three sources
   - Save to JSON file
   - Provide summary statistics

I decided to start with the individual fetchers first, then build the normalization layer, and finally create the main orchestrator. This bottom-up approach let me test each component independently.

## AI Prompts Used

### Initial Setup - NewsAPI Fetcher

**Prompt 1:**
```
Write a Python function called fetch_newsapi() that:
- Takes api_key and query as parameters
- Fetches top 10 articles from NewsAPI
- Returns a list of dicts with keys: title, content, source, url, fetched_at
- Handles: rate limits (429 errors), timeouts (5 sec), auth errors (401)
- Uses requests library with proper timeout
- Includes try-except with specific error messages
- Returns empty list on failure with logged error
```

This got me the basic structure. I noticed the function was using `/v2/everything` endpoint which seemed right for searching. The timeout handling looked good, but I had to verify the error codes matched NewsAPI's actual behavior.

### CSV Reader Implementation

**Prompt 2:**
```
Write a Python function called read_csv() that:
- Takes file_path as parameter
- Reads CSV with columns: title, content, source, url
- Returns list of dicts matching the standard format
- Handles: FileNotFoundError, encoding errors (try utf-8, latin-1), empty files
- Uses pandas or csv library
- Validates required columns exist
- Adds fetched_at timestamp
- Returns empty list with logged error on failure
```

I went with pandas here because:
- It handles encoding issues more gracefully than the csv module
- Better error messages when columns are missing
- Easier to work with if we need to do any data transformations later
- The csv module would require more manual error handling

The encoding fallback (utf-8 → latin-1) was important because I've seen CSV files from different systems use different encodings. This saved me debugging time later.

### Web Scraper

**Prompt 3:**
```
Write a Python function called scrape_website() that:
- Takes url as parameter
- Scrapes articles from the webpage
- Extracts: title (h1 or h2), content (paragraphs), source (domain name)
- Returns list of dicts in standard format
- Handles: connection timeout (10 sec), 404 errors, parsing failures
- Uses BeautifulSoup and requests
- Includes User-Agent header
- Returns empty list with logged error on failure
```

I chose BeautifulSoup over alternatives like lxml or html.parser directly because:
- More forgiving with malformed HTML (real websites are messy)
- Easier API for finding elements
- Good documentation and community support
- Works well with requests library

The User-Agent header was crucial - without it, many sites block requests. I used a standard Chrome user agent string to avoid looking like a bot.

### Normalization Function

**Prompt 4:**
```
In fetchers/common.py with:
1. normalize_article(raw_data, source) function
2. Ensures consistent output format
3. Handles missing fields gracefully
4. Adds ISO 8601 timestamp if missing
5. Type hints and docstrings

Output format required:
{title, content, source, url, fetched_at}
```

This was interesting - I realized different sources might use different field names. NewsAPI uses "description" as a fallback for "content", CSV might have different column names, etc. The normalize function needed to be flexible but still enforce the standard format.

### Main Orchestrator

**Prompt 5:**
```
In main.py that:
1. Imports all 3 fetchers
2. Runs them with error handling
3. Combines results
4. Creates output/ directory if missing
5. Saves to output/articles.json
6. Prints summary
7. Uses logging, not print
```

The main function needed to be resilient - if one fetcher fails, the others should still run. I used separate try-except blocks for each fetcher so failures don't cascade.

## Iterations and Improvements

### First Iteration: Basic Error Handling

Initially, I had basic try-except blocks but wasn't catching specific exceptions. For example, in the NewsAPI function, I was catching all exceptions the same way. I refined this to:

- `requests.exceptions.Timeout` - specific timeout handling
- `requests.exceptions.RequestException` - general request errors
- Status code checks (429, 401) before trying to parse JSON

This made debugging much easier because I could see exactly what went wrong.

### Second Iteration: Encoding Issues in CSV Reader

First version only tried utf-8. When I tested with a CSV file that had special characters (probably exported from Excel on Windows), it failed. Added the latin-1 fallback:

```python
encodings = ["utf-8", "latin-1"]
for encoding in encodings:
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        break
    except UnicodeDecodeError:
        continue
```

This handles most real-world CSV files I've encountered.

### Third Iteration: Web Scraper Title Extraction

The initial version only looked for h1 tags. But some news sites use h2 for article titles, or have multiple h1 tags (one for site header, one for article). I added fallback logic:

1. Try h1 first
2. If no h1, try h2
3. If still nothing, try `<title>` tag
4. Last resort: og:title meta tag

This makes the scraper more robust across different website structures.

### Fourth Iteration: Timestamp Handling

Initially, I was generating a new timestamp for every article, even if the source provided one. I updated `normalize_article()` to:
- Use existing timestamp if present and valid
- Parse and normalize to ISO 8601 format
- Only generate new timestamp if missing or invalid

This preserves original publication dates when available, which is more useful than overwriting everything.

### Fifth Iteration: Output Format Validation

Added explicit checks in the normalize function to ensure all values are strings. Some APIs return None for missing fields, and I needed to convert those to empty strings for consistency:

```python
title = str(title) if title is not None else ""
```

This prevents JSON serialization issues and ensures the output is always predictable.

## Key Decisions

### Why pandas for CSV reading?

I considered the standard `csv` module, but pandas won because:
- **Better error handling**: pandas gives clear error messages when columns are missing
- **Encoding support**: Built-in encoding detection and handling
- **Data validation**: Easy to check for empty DataFrames
- **Future-proof**: If we need to do any data cleaning or transformation, pandas makes it easier

The trade-off is an extra dependency, but pandas is so commonly used in data projects that it's worth it.

### Why BeautifulSoup for web scraping?

Alternatives considered:
- **lxml**: Faster, but less forgiving with bad HTML
- **html.parser**: Built-in, but less powerful API
- **regex**: Just... no. HTML isn't regular.

BeautifulSoup's `find()` and `find_all()` methods are intuitive, and it handles malformed HTML gracefully. Real websites have broken HTML, and BeautifulSoup doesn't choke on it.

### Why separate normalization function?

I could have had each fetcher return the exact format, but a separate `normalize_article()` function:
- **Centralizes format logic**: One place to change if requirements change
- **Handles edge cases**: Different sources use different field names
- **Reusable**: Can normalize data from any source, not just the three fetchers
- **Testable**: Easy to unit test normalization logic separately

### Why 5-second timeout for NewsAPI but 10-second for web scraping?

NewsAPI is a fast REST API - if it takes more than 5 seconds, something is wrong. Web scraping is inherently slower:
- Larger HTML payloads
- Network latency
- Server response times vary more

10 seconds gives legitimate slow sites a chance while still catching actual timeouts.

### Why return empty list on failure?

Instead of raising exceptions, all functions return `[]` on failure. This allows:
- **Graceful degradation**: Main function can continue even if one source fails
- **Simpler error handling**: Callers don't need try-except blocks
- **Consistent API**: All fetchers have the same return type

The downside is that callers need to check the length, but for this use case (aggregating from multiple sources), it works well.

## Challenges Faced

### Challenge 1: NewsAPI Response Format Variations

NewsAPI sometimes returns `content` as `None` and puts the text in `description` instead. I had to handle this:

```python
"content": article.get("content", "") or article.get("description", "")
```

The `or` operator handles both `None` and empty string cases.

### Challenge 2: CSV Column Validation

Early version would crash if a column was missing. I added explicit validation:

```python
missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
if missing_columns:
    logger.error(f"Missing required columns: {', '.join(missing_columns)}")
    return []
```

This gives clear error messages instead of cryptic KeyErrors.

### Challenge 3: Web Scraper Blocking

Some sites block requests without a User-Agent header. I added a standard browser User-Agent:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."
}
```

This makes requests look like they're coming from a real browser.

### Challenge 4: Timestamp Format Consistency

Different sources might provide timestamps in different formats. I needed to normalize them all to ISO 8601. The `datetime.fromisoformat()` method helps, but I had to handle edge cases like:
- Timestamps with 'Z' suffix (UTC indicator)
- Already-formatted strings
- datetime objects
- Missing timestamps

### Challenge 5: Testing with Mocks

Writing tests for the NewsAPI function required mocking `requests.get`. I used `unittest.mock.patch`:

```python
@patch('fetchers.newsapi.requests.get')
def test_successful_fetch(self, mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {...}
    mock_get.return_value = mock_response
```

The key was patching `'fetchers.newsapi.requests.get'` (the imported reference) not `'requests.get'` (the original). This is a common gotcha with mocking.

## What I Learned

1. **Error handling is more nuanced than I thought**: Different error types need different handling. A 429 (rate limit) is different from a 401 (auth error), and both are different from a timeout.

2. **Encoding matters**: Real-world CSV files come in different encodings. Always have a fallback strategy.

3. **Web scraping is fragile**: Websites change their HTML structure. Having multiple fallback strategies (h1 → h2 → title tag) makes scrapers more resilient.

4. **Logging > print**: Using logging instead of print statements makes it easier to:
   - Control output levels (INFO, WARNING, ERROR)
   - Add timestamps automatically
   - Redirect to files if needed
   - Filter messages in production

5. **Type hints help catch bugs early**: Even without a strict type checker, type hints serve as documentation and help catch mismatches during development.

6. **Mocking requires understanding imports**: When mocking, you need to patch where the object is used, not where it's defined. This is the "mock where you use, not where you import" principle.

7. **Empty lists are better than None**: Returning `[]` instead of `None` makes the API more consistent. Callers can always iterate, even if the list is empty.

8. **ISO 8601 timestamps are worth it**: Using ISO 8601 format makes timestamps:
   - Sortable as strings
   - Parseable by most systems
   - Human-readable
   - Timezone-aware (if you include timezone info)

9. **User-Agent headers matter**: Many sites block requests without proper User-Agent strings. Always include one that looks like a real browser.

10. **Graceful degradation beats perfect failure**: If one data source fails, the system should continue with the others. This makes the system more robust in production.

## Final Thoughts

This project reinforced that real-world code needs to handle edge cases and failures gracefully. The "happy path" is easy - it's the error cases that make or break a system. Spending time on proper error handling, logging, and validation pays off when things go wrong (and they will).

The modular structure (separate fetchers, normalization function, main orchestrator) made testing easier and the code more maintainable. If I need to add a fourth data source, I can just create a new fetcher and add it to main.py without touching the existing code.
