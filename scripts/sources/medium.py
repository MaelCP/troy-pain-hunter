import time
import requests
from bs4 import BeautifulSoup

FEED_BASE = "https://medium.com/feed/tag/"
HEADERS = {"User-Agent": "troy-pain-hunter/1.0"}
RESULTS_PER_KEYWORD = 5


def _slug(keyword: str) -> str:
    return keyword.lower().strip().replace(" ", "-")


def fetch_medium(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                FEED_BASE + _slug(keyword),
                headers=HEADERS,
                timeout=10,
            )
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")[:RESULTS_PER_KEYWORD]
            for item in items:
                title = (item.title.text if item.title else "").strip()
                link = (item.link.text if item.link else "").strip()
                if not title or not link:
                    continue
                pub = item.find("pubDate")
                results.append({
                    "source": "medium",
                    "url": link,
                    "text": title[:500],
                    "score": 0,
                    "lang": "en",
                    "published_at": pub.text.strip() if pub else None,
                })
            time.sleep(1)
        except Exception:
            continue
    return results
