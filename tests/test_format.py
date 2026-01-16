#!/usr/bin/env python3
"""
Quick test script to verify the project is working.
Run this after setting up to check if everything works.
"""

import json
import os
from fetchers.csv_reader import read_csv

def test_csv_reader():
    """Test CSV reader with sample file."""
    print("Testing CSV reader...")
    csv_path = "data/articles.csv"
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return False
    
    articles = read_csv(csv_path)
    
    if not articles:
        print("❌ No articles returned from CSV reader")
        return False
    
    print(f"✅ CSV reader returned {len(articles)} articles")
    
    # Check format
    required_keys = {"title", "content", "source", "url", "fetched_at"}
    for article in articles:
        if set(article.keys()) != required_keys:
            print(f"❌ Article missing required keys: {set(article.keys())}")
            return False
        if article["source"] != "csv":
            print(f"❌ Source should be 'csv', got: {article['source']}")
            return False
    
    print("✅ CSV reader format is correct")
    return True

def test_output_format():
    """Test if output/articles.json has correct format."""
    print("\nTesting output format...")
    output_file = "output/articles.json"
    
    if not os.path.exists(output_file):
        print(f"⚠️  Output file not found. Run main.py first.")
        return False
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            articles = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    
    if not isinstance(articles, list):
        print(f"❌ Output should be a list, got: {type(articles)}")
        return False
    
    print(f"✅ Output file contains {len(articles)} articles")
    
    if articles:
        required_keys = {"title", "content", "source", "url", "fetched_at"}
        article = articles[0]
        
        if set(article.keys()) != required_keys:
            print(f"❌ Article missing required keys")
            print(f"   Expected: {required_keys}")
            print(f"   Got: {set(article.keys())}")
            return False
        
        # Check timestamp format
        fetched_at = article.get("fetched_at", "")
        if not fetched_at.endswith("Z"):
            print(f"⚠️  Timestamp should end with 'Z' (UTC), got: {fetched_at}")
        
        print("✅ Output format is correct")
        print(f"\nSample article:")
        print(json.dumps(article, indent=2))
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Quick Test Script")
    print("=" * 60)
    
    csv_ok = test_csv_reader()
    output_ok = test_output_format()
    
    print("\n" + "=" * 60)
    if csv_ok and output_ok:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("=" * 60)
