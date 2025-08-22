#!/usr/bin/env python
"""
Test script for NewsAPI functionality
"""

import os
import sys
import requests
from urllib.parse import urlencode

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from scripts.utils import load_yaml


def test_newsapi():
    """Test NewsAPI functionality"""

    # Check if API key is set
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        print("❌ NEWS_API_KEY not set in environment")
        print("Please set it with: export NEWS_API_KEY='your_api_key_here'")
        return False

    print(f"✅ NEWS_API_KEY found: {api_key[:10]}...")

    # Load configuration
    try:
        cfg = load_yaml("config/sources.yaml")
        newsapi_cfg = cfg.get("newsapi", {})
        print(f"✅ NewsAPI config loaded: {newsapi_cfg}")
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False

    # Test API call
    try:
        params = {
            "q": newsapi_cfg.get("query", "artificial intelligence"),
            "language": newsapi_cfg.get("language", "en"),
            "pageSize": int(newsapi_cfg.get("page_size", 50)),
            "sortBy": "publishedAt",
        }

        url = "https://newsapi.org/v2/everything?" + urlencode(params)
        headers = {"X-Api-Key": api_key}

        print(f"🔍 Testing URL: {url}")
        print(f"📝 Query: {params['q']}")

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            total_results = data.get("totalResults", 0)
            articles = data.get("articles", [])

            print(f"✅ NewsAPI test successful!")
            print(f"📊 Total results: {total_results}")
            print(f"📰 Articles returned: {len(articles)}")

            if articles:
                print("\n📋 Sample articles:")
                for i, article in enumerate(articles[:3], 1):
                    title = article.get("title", "No title")
                    source = (article.get("source") or {}).get("name", "Unknown")
                    published = article.get("publishedAt", "Unknown date")
                    print(f"  {i}. {title}")
                    print(f"     Source: {source} | Date: {published}")
                    print()

            return True

        else:
            print(f"❌ NewsAPI request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_with_sample_key():
    """Test with a sample API key to check if the endpoint is working"""
    print("\n🔧 Testing NewsAPI endpoint with sample key...")

    try:
        # Test with a dummy key to see the error response
        params = {
            "q": "artificial intelligence",
            "language": "en",
            "pageSize": 5,
            "sortBy": "publishedAt",
        }

        url = "https://newsapi.org/v2/everything?" + urlencode(params)
        headers = {"X-Api-Key": "test_key"}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 401:
            print("✅ NewsAPI endpoint is accessible (expected 401 with test key)")
            print("This means the service is working, you just need a valid API key")
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")

    except Exception as e:
        print(f"❌ Cannot reach NewsAPI: {e}")


if __name__ == "__main__":
    print("🧪 NewsAPI Test Script")
    print("=" * 50)

    success = test_newsapi()

    if not success:
        test_with_sample_key()

    print("\n📝 To get a NewsAPI key:")
    print("1. Go to https://newsapi.org/")
    print("2. Sign up for a free account")
    print("3. Get your API key from the dashboard")
    print("4. Set it with: export NEWS_API_KEY='your_key_here'")
    print("5. Run this test again")
