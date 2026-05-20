import time
import requests

API_BASE = "https://dev.to/api/articles"
RESULTS_PER_KEYWORD = 5


def fetch_devto(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                API_BASE,
                params={
                    "tag": keyword.lower().replace(" ", ""),
                    "per_page": RESULTS_PER_KEYWORD,
                    "top": 30,
                },
                timeout=10,
            )
            data = response.json()
            if not isinstance(data, list):
                continue
            for item in data:
                text = item.get("title", "") or item.get("description", "")
                if not text.strip():
                    continue
                results.append({
                    "source": "devto",
                    "url": item.get("url", ""),
                    "text": text[:500],
                    "score": item.get("public_reactions_count", 0),
                    "lang": "en",
                    "published_at": item.get("published_at"),
                })
            time.sleep(1)
        except Exception:
            continue
    return results
