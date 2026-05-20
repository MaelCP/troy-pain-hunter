import time
import requests

API_BASE = "https://api.github.com/search/issues"
HEADERS = {
    "User-Agent": "troy-pain-hunter/1.0",
    "Accept": "application/vnd.github+json",
}
RESULTS_PER_KEYWORD = 5


def fetch_github(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                API_BASE,
                params={
                    "q": f'{keyword} in:title,body state:open',
                    "sort": "reactions",
                    "order": "desc",
                    "per_page": RESULTS_PER_KEYWORD,
                },
                headers=HEADERS,
                timeout=10,
            )
            data = response.json()
            for item in data.get("items", []):
                text = item.get("title", "") or item.get("body", "") or ""
                if not text.strip():
                    continue
                results.append({
                    "source": "github",
                    "url": item.get("html_url", ""),
                    "text": text[:500],
                    "score": item.get("reactions", {}).get("total_count", 0),
                    "lang": "en",
                    "published_at": item.get("created_at"),
                })
            time.sleep(2)
        except Exception:
            continue
    return results
