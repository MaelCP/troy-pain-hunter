import time
import requests

SEARCH_BASE = "https://lobste.rs/search.json"
HEADERS = {"User-Agent": "troy-pain-hunter/1.0"}
RESULTS_PER_KEYWORD = 5


def fetch_lobsters(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                SEARCH_BASE,
                params={"q": keyword, "what": "stories", "order": "relevance"},
                headers=HEADERS,
                timeout=10,
            )
            try:
                data = response.json()
            except Exception:
                continue
            items = data if isinstance(data, list) else data.get("stories", [])
            for item in items[:RESULTS_PER_KEYWORD]:
                text = item.get("title", "")
                if not text.strip():
                    continue
                results.append({
                    "source": "lobsters",
                    "url": item.get("short_id_url") or item.get("url", ""),
                    "text": text[:500],
                    "score": item.get("score", 0),
                    "lang": "en",
                    "published_at": item.get("created_at"),
                })
            time.sleep(1)
        except Exception:
            continue
    return results
