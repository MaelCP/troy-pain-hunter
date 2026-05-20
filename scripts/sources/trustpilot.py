import time
import requests
from bs4 import BeautifulSoup

SEARCH_BASE = "https://www.trustpilot.com/search"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
RESULTS_PER_KEYWORD = 5


def fetch_trustpilot(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            response = requests.get(
                SEARCH_BASE,
                params={"query": keyword},
                headers=HEADERS,
                timeout=10,
            )
            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.select("a[href^='/review/']")
            seen = set()
            count = 0
            for a in cards:
                if count >= RESULTS_PER_KEYWORD:
                    break
                href = a.get("href", "")
                if not href or href in seen:
                    continue
                seen.add(href)
                text = a.get_text(" ", strip=True)
                if not text or len(text) < 4:
                    continue
                results.append({
                    "source": "trustpilot",
                    "url": f"https://www.trustpilot.com{href}",
                    "text": text[:500],
                    "score": 0,
                    "lang": "en",
                })
                count += 1
            time.sleep(2)
        except Exception:
            continue
    return results
