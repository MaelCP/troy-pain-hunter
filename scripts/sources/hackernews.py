import time
import requests

ALGOLIA_BASE = "https://hn.algolia.com/api/v1/search"
RESULTS_PER_KEYWORD = 5


def fetch_hackernews(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                ALGOLIA_BASE,
                params={
                    "query": keyword,
                    "tags": "story",
                    "hitsPerPage": RESULTS_PER_KEYWORD,
                },
                timeout=10,
            )
            data = response.json()
            for hit in data.get("hits", []):
                text = hit.get("title", "") or hit.get("story_text", "")
                if not text.strip():
                    continue
                object_id = hit.get("objectID")
                results.append({
                    "source": "hackernews",
                    "url": f"https://news.ycombinator.com/item?id={object_id}",
                    "text": text[:500],
                    "score": hit.get("points") or 0,
                    "lang": "en",
                    "published_at": hit.get("created_at"),
                })
            time.sleep(1)
        except Exception:
            continue
    return results
