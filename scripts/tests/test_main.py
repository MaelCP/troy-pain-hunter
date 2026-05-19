from unittest.mock import patch, MagicMock
import json
from main import aggregate, deduplicate, resolve_scopes, run

SAMPLE_RESULTS = [
    {"source": "reddit", "url": "https://reddit.com/r/a", "text": "hate", "score": 500, "lang": "en", "scope": "saas", "scraped_at": "2026-05-19T10:00:00"},
    {"source": "google", "url": "https://reddit.com/r/a", "text": "hate", "score": 0, "lang": "en", "scope": "saas", "scraped_at": "2026-05-19T10:00:00"},
    {"source": "twitter", "url": "https://twitter.com/b", "text": "annoying", "score": 200, "lang": "en", "scope": "saas", "scraped_at": "2026-05-19T10:00:00"},
]


def test_deduplicate_removes_same_url():
    deduped = deduplicate(SAMPLE_RESULTS)
    urls = [r["url"] for r in deduped]
    assert len(urls) == len(set(urls))


def test_aggregate_sorts_by_score_descending():
    deduped = deduplicate(SAMPLE_RESULTS)
    assert deduped[0]["score"] >= deduped[-1]["score"]


def test_resolve_scopes_all_returns_four():
    scopes = resolve_scopes(["all"])
    assert set(scopes) == {"annoying", "saas", "physical", "freelance"}


def test_resolve_scopes_single():
    assert resolve_scopes(["saas"]) == ["saas"]


def test_resolve_scopes_multiple():
    assert set(resolve_scopes(["saas", "annoying"])) == {"saas", "annoying"}


def test_resolve_scopes_unknown_raises():
    try:
        resolve_scopes(["unknown_scope"])
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "unknown_scope" in str(e)
        assert "annoying" in str(e)


def test_run_returns_valid_json_structure():
    mock_results = [
        {"source": "reddit", "url": "https://reddit.com/1", "text": "hate doing this", "score": 100, "lang": "en"}
    ]
    mock_mem = MagicMock()
    mock_mem.seen_url.return_value = False
    mock_mem.save_results.return_value = 1
    with patch("main.fetch_reddit", return_value=mock_results), \
         patch("main.fetch_google", return_value=[]), \
         patch("main.fetch_twitter", return_value=[]), \
         patch("main.fetch_facebook", return_value=[]), \
         patch("main.TroyMemory", return_value=mock_mem):
        output = run(scopes=["annoying"])
    data = json.loads(output)
    assert "results" in data
    assert "errors" in data
    assert "by_scope" in data
    assert "new_results" in data
    assert "already_seen" in data


def test_run_skips_already_seen_url():
    mock_results = [
        {"source": "reddit", "url": "https://already-seen.com", "text": "t", "score": 10, "lang": "en"}
    ]
    mock_mem = MagicMock()
    mock_mem.seen_url.return_value = True
    mock_mem.save_results.return_value = 0
    with patch("main.fetch_reddit", return_value=mock_results), \
         patch("main.fetch_google", return_value=[]), \
         patch("main.fetch_twitter", return_value=[]), \
         patch("main.fetch_facebook", return_value=[]), \
         patch("main.TroyMemory", return_value=mock_mem):
        output = run(scopes=["annoying"])
    data = json.loads(output)
    assert data["already_seen"] == 1
    assert data["new_results"] == 0


def test_run_by_scope_counts():
    mock_mem = MagicMock()
    mock_mem.seen_url.return_value = False
    mock_mem.save_results.return_value = 2
    with patch("main.fetch_reddit", return_value=[
        {"source": "reddit", "url": "https://a.com", "text": "t", "score": 1, "lang": "en"},
        {"source": "reddit", "url": "https://b.com", "text": "t", "score": 2, "lang": "en"},
    ]), \
         patch("main.fetch_google", return_value=[]), \
         patch("main.fetch_twitter", return_value=[]), \
         patch("main.fetch_facebook", return_value=[]), \
         patch("main.TroyMemory", return_value=mock_mem):
        output = run(scopes=["saas"])
    data = json.loads(output)
    assert "saas" in data["by_scope"]


def test_run_reports_missing_env_tokens(monkeypatch):
    monkeypatch.delenv("TWITTER_BEARER_TOKEN", raising=False)
    monkeypatch.delenv("FACEBOOK_ACCESS_TOKEN", raising=False)
    mock_mem = MagicMock()
    mock_mem.seen_url.return_value = False
    mock_mem.save_results.return_value = 0
    with patch("main.fetch_reddit", return_value=[]), \
         patch("main.fetch_google", return_value=[]), \
         patch("main.TroyMemory", return_value=mock_mem):
        output = run(scopes=["annoying"])
    data = json.loads(output)
    assert any("TWITTER_BEARER_TOKEN" in e for e in data["errors"])
    assert any("FACEBOOK_ACCESS_TOKEN" in e for e in data["errors"])
