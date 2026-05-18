from unittest.mock import patch
from sources.google import fetch_google

def test_fetch_google_returns_normalized_results():
    mock_urls = [
        "https://reddit.com/r/smallbusiness/post1",
        "https://forums.example.com/thread/annoying-task",
    ]
    with patch("sources.google.search", return_value=iter(mock_urls)):
        results = fetch_google(["annoying thing to do"])
    assert len(results) == 2
    assert results[0]["source"] == "google"
    assert results[0]["url"] == mock_urls[0]
    assert results[0]["score"] == 0
    assert results[0]["text"] != ""

def test_fetch_google_returns_empty_on_error():
    with patch("sources.google.search", side_effect=Exception("rate limit")):
        results = fetch_google(["annoying"])
    assert results == []
