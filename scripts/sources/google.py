import time
from googlesearch import search

RESULTS_PER_KEYWORD = 5


def fetch_google(keywords: list[str]) -> list[dict]:
    results = []
    for keyword in keywords:
        try:
            urls = list(search(keyword, num_results=RESULTS_PER_KEYWORD, lang="en"))
            for url in urls:
                results.append({
                    "source": "google",
                    "url": url,
                    "text": f"[Google result] {keyword} — {url}",
                    "score": 0,
                    "lang": "en",
                })
            time.sleep(2)
        except Exception:
            continue
    return results
