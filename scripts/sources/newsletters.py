import time
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "troy-pain-hunter/1.0"}
MAX_ITEMS_PER_FEED = 20

NEWSLETTER_FEEDS = [
    ("lenny", "https://www.lennysnewsletter.com/feed"),
    ("pragmatic-engineer", "https://newsletter.pragmaticengineer.com/feed"),
    ("stratechery", "https://stratechery.com/feed/"),
    ("not-boring", "https://www.notboring.co/feed"),
    ("indiehackers", "https://www.indiehackers.com/feed.xml"),
    ("the-hustle", "https://thehustle.co/feed/"),
    ("microacquire", "https://acquire.com/blog/feed/"),
]


def _matches(text: str, keywords: list[str]) -> bool:
    low = text.lower()
    return any(k.lower() in low for k in keywords)


def fetch_newsletters(keywords: list[str]) -> list[dict]:
    results = []
    for label, feed_url in NEWSLETTER_FEEDS:
        try:
            response = requests.get(feed_url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")[:MAX_ITEMS_PER_FEED]
            for item in items:
                title = (item.title.text if item.title else "").strip()
                link = (item.link.text if item.link else "").strip()
                desc = (item.description.text if item.description else "").strip()
                blob = f"{title} {desc}"
                if not title or not link or not _matches(blob, keywords):
                    continue
                pub = item.find("pubDate")
                results.append({
                    "source": f"newsletter-{label}",
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
