from unittest.mock import patch, MagicMock
from sources.twitter import fetch_twitter

def test_fetch_twitter_returns_normalized_results():
    mock_tweet = MagicMock()
    mock_tweet.text = "I hate having to manually update spreadsheets every Monday"
    mock_tweet.id = "123456789"
    mock_tweet.public_metrics = {"like_count": 42, "retweet_count": 5}

    mock_response = MagicMock()
    mock_response.data = [mock_tweet]

    with patch("sources.twitter.tweepy.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.search_recent_tweets.return_value = mock_response
        results = fetch_twitter(["I hate having to"], bearer_token="fake_token")

    assert len(results) == 1
    assert results[0]["source"] == "twitter"
    assert results[0]["score"] == 47
    assert "twitter.com" in results[0]["url"]

def test_fetch_twitter_returns_empty_when_no_token():
    results = fetch_twitter(["annoying"], bearer_token=None)
    assert results == []

def test_fetch_twitter_returns_empty_on_api_error():
    with patch("sources.twitter.tweepy.Client") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_client.search_recent_tweets.side_effect = Exception("401 Unauthorized")
        results = fetch_twitter(["annoying"], bearer_token="bad_token")
    assert results == []
