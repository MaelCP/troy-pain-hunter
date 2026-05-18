import time
import requests

REDDIT_BASE = "https://www.reddit.com/search.json"
HEADERS = {"User-Agent": "troy-pain-hunter/1.0"}
RESULTS_PER_KEYWORD = 5


def fetch_reddit(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                REDDIT_BASE,
                params={"q": keyword, "sort": "hot", "limit": RESULTS_PER_KEYWORD},
                headers=HEADERS,
                timeout=10,
            )
            data = response.json()
            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                text = post.get("title", "") or post.get("selftext", "")
                if not text.strip():
                    continue
                results.append({
                    "source": "reddit",
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "text": text[:500],
                    "score": post.get("score", 0),
                    "lang": "en",
                })
            time.sleep(1)
        except Exception:
            continue
    return results
