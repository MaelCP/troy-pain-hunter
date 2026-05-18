from unittest.mock import patch
from sources.facebook import fetch_facebook

MOCK_FB_RESPONSE = {
    "data": [
        {
            "id": "post_001",
            "message": "Tâche chiante : devoir refaire les SOP à chaque nouvelle embauche.",
            "story": "",
            "created_time": "2026-05-10T10:00:00+0000",
        }
    ]
}

def test_fetch_facebook_returns_normalized_results():
    with patch("sources.facebook.requests.get") as mock_get:
        mock_get.return_value.json.return_value = MOCK_FB_RESPONSE
        mock_get.return_value.status_code = 200
        results = fetch_facebook(["tâche chiante"], access_token="fake_token")
    assert len(results) == 1
    assert results[0]["source"] == "facebook"
    assert results[0]["score"] == 0
    assert "tâche chiante" in results[0]["text"].lower()

def test_fetch_facebook_returns_empty_when_no_token():
    results = fetch_facebook(["annoying"], access_token=None)
    assert results == []

def test_fetch_facebook_returns_empty_on_api_error():
    with patch("sources.facebook.requests.get") as mock_get:
        mock_get.side_effect = Exception("403 Forbidden")
        results = fetch_facebook(["annoying"], access_token="bad_token")
    assert results == []
