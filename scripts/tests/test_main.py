from unittest.mock import patch
import json
from main import aggregate, deduplicate, run

SAMPLE_RESULTS = [
    {"source": "reddit", "url": "https://reddit.com/r/a", "text": "I hate having to do X", "score": 500, "lang": "en"},
    {"source": "google", "url": "https://reddit.com/r/a", "text": "I hate having to do X", "score": 0, "lang": "en"},
    {"source": "twitter", "url": "https://twitter.com/b", "text": "annoying task at work", "score": 200, "lang": "en"},
]

def test_deduplicate_removes_same_url():
    deduped = deduplicate(SAMPLE_RESULTS)
    urls = [r["url"] for r in deduped]
    assert len(urls) == len(set(urls))

def test_aggregate_sorts_by_score_descending():
    deduped = deduplicate(SAMPLE_RESULTS)
    assert deduped[0]["score"] >= deduped[-1]["score"]

def test_run_returns_valid_json_structure():
    mock_results = [
        {"source": "reddit", "url": "https://reddit.com/1", "text": "hate doing this", "score": 100, "lang": "en"}
    ]
    with patch("main.fetch_reddit", return_value=mock_results), \
         patch("main.fetch_google", return_value=[]), \
         patch("main.fetch_twitter", return_value=[]), \
         patch("main.fetch_facebook", return_value=[]):
        output = run()
    data = json.loads(output)
    assert "results" in data
    assert "errors" in data
    assert "sources_used" in data
    assert "total" in data
    assert data["total"] == 1

def test_run_reports_missing_env_tokens(monkeypatch):
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("FACEBOOK_ACCESS_TOKEN", raising=False)
    with patch("main.fetch_reddit", return_value=[]), \
         patch("main.fetch_google", return_value=[]):
        output = run()
    data = json.loads(output)
    assert any("TWITTER_BEARER_TOKEN" in e for e in data["errors"])
    assert any("FACEBOOK_ACCESS_TOKEN" in e for e in data["errors"])
