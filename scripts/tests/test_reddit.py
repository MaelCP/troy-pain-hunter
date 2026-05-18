from unittest.mock import patch, MagicMock
import pytest
from sources.reddit import fetch_reddit

MOCK_RESPONSE = {
    "data": {
        "children": [
            {
                "data": {
                    "title": "I hate having to manually sync inventory with TikTok Shop",
                    "selftext": "It takes forever and there's no affordable tool.",
                    "permalink": "/r/smallbusiness/comments/abc123/title/",
                    "score": 890,
                }
            },
            {
                "data": {
                    "title": "So frustrating when clients don't read the brief",
                    "selftext": "",
                    "permalink": "/r/freelance/comments/def456/title/",
                    "score": 340,
                }
            },
        ]
    }
}

def test_fetch_reddit_returns_normalized_results():
    with patch("sources.reddit.requests.get") as mock_get:
        mock_get.return_value.json.return_value = MOCK_RESPONSE
        mock_get.return_value.status_code = 200
        results = fetch_reddit(["I hate having to"])
    assert len(results) == 2
    assert results[0]["source"] == "reddit"
    assert results[0]["score"] == 890
    assert "reddit.com" in results[0]["url"]
    assert results[0]["text"] != ""

def test_fetch_reddit_returns_empty_on_http_error():
    with patch("sources.reddit.requests.get") as mock_get:
        mock_get.side_effect = Exception("Connection error")
        results = fetch_reddit(["I hate having to"])
    assert results == []

def test_fetch_reddit_skips_empty_text():
    mock_with_empty = {
        "data": {
            "children": [
                {"data": {"title": "", "selftext": "", "permalink": "/r/test/", "score": 10}}
            ]
        }
    }
    with patch("sources.reddit.requests.get") as mock_get:
        mock_get.return_value.json.return_value = mock_with_empty
        mock_get.return_value.status_code = 200
        results = fetch_reddit(["annoying"])
    assert results == []
