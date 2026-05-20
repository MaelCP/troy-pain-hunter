import time
import requests
from bs4 import BeautifulSoup

SEARCH_BASE = "https://www.indiehackers.com/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
RESULTS_PER_KEYWORD = 5


def fetch_indiehackers(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                SEARCH_BASE,
                params={"q": keyword, "type": "post"},
                headers=HEADERS,
                timeout=10,
            )
            soup = BeautifulSoup(response.text, "html.parser")
            posts = soup.select("a.feed-item__title-link, a.search-result__link, a[href^='/post/']")
            count = 0
            seen = set()
            for a in posts:
                if count >= RESULTS_PER_KEYWORD:
                    break
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                seen.add(href)
                text = a.get_text(strip=True)
                if not text:
                    continue
                url = href if href.startswith("http") else f"https://www.indiehackers.com{href}"
                results.append({
                    "source": "indiehackers",
                    "url": url,
                    "text": text[:500],
                    "score": 0,
                    "lang": "en",
                })
                count += 1
            time.sleep(2)
        except Exception:
            continue
    return results
