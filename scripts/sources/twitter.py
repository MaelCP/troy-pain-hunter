import time
import tweepy

RESULTS_PER_KEYWORD = 5


def fetch_twitter(keywords: list[str], bearer_token: str | None) -> list[dict]:
    if not bearer_token:
        return []

    client = tweepy.Client(bearer_token=bearer_token)
    results = []

    for keyword in keywords:
        try:
            response = client.search_recent_tweets(
                query=f"{keyword} -is:retweet lang:en",
                max_results=RESULTS_PER_KEYWORD,
                tweet_fields=["public_metrics"],
            )
            if not response.data:
                continue
            for tweet in response.data:
                metrics = tweet.public_metrics or {}
                score = metrics.get("like_count", 0) + metrics.get("retweet_count", 0)
                results.append({
                    "source": "twitter",
                    "url": f"https://twitter.com/i/web/status/{tweet.id}",
                    "text": tweet.text[:500],
                    "score": score,
                    "lang": "en",
                })
            time.sleep(1)
        except Exception:
            continue

    return results
