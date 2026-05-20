import time
import requests

API_BASE = "https://api.stackexchange.com/2.3/search/advanced"
SITES = ["stackoverflow", "softwareengineering", "superuser"]
RESULTS_PER_KEYWORD = 5


def fetch_stackexchange(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        for site in SITES:
            try:
                response = requests.get(
                    API_BASE,
                    params={
                        "order": "desc",
                        "sort": "votes",
                        "q": keyword,
                        "site": site,
                        "pagesize": RESULTS_PER_KEYWORD,
                    },
                    timeout=10,
                )
                data = response.json()
                for item in data.get("items", []):
                    text = item.get("title", "")
                    if not text.strip():
                        continue
                    from datetime import datetime, timezone
                    cd = item.get("creation_date")
                    published_at = (
                        datetime.fromtimestamp(cd, tz=timezone.utc).isoformat()
                        if cd else None
                    )
                    results.append({
                        "source": f"stackexchange-{site}",
                        "url": item.get("link", ""),
                        "text": text[:500],
                        "score": item.get("score", 0),
                        "lang": "en",
                        "published_at": published_at,
                    })
                time.sleep(1)
            except Exception:
                continue
    return results
