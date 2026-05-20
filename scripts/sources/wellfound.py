"""Wellfound (ex-AngelList) — startup jobs, signal très différent.

Les offres Wellfound sont surtout US/UK et orientées tech early-stage : un
proxy excellent pour repérer les segments où l'IA crée des opportunités SaaS.

Wellfound est anti-scrape côté direct ; on passe par DuckDuckGo `site:` comme
fallback (cf google_jobs.py pour le pattern).
"""

import re
import time
from urllib.parse import urlparse, unquote, quote

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html",
}
RESULTS_PER_KEYWORD = 6


def fetch_wellfound(keywords: list[str]) -> list[dict]:
    results: list[dict] = []
    seen: set[str] = set()
    for kw in keywords:
        try:
            q = quote(f"site:wellfound.com {kw}")
            r = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": f"site:wellfound.com {kw}"},
                headers=HEADERS,
                timeout=12,
            )
            if r.status_code != 200:
                continue
            pairs = re.findall(
                r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                r.text,
                re.S,
            )
            for href, title in pairs[:RESULTS_PER_KEYWORD]:
                m = re.search(r"uddg=([^&]+)", href)
                if m:
                    href = unquote(m.group(1))
                p = urlparse(href)
                if "wellfound.com" not in p.netloc:
                    continue
                if href in seen:
                    continue
                seen.add(href)
                title_clean = re.sub(r"<[^>]+>", "", title).strip()
                if not title_clean:
                    continue
                results.append({
                    "source": "wellfound",
                    "url": href.split("?")[0],
                    "text": title_clean[:400],
                    "score": 0,
                    "lang": "en",
                    "published_at": None,
                })
            time.sleep(2)
        except Exception:
            continue
    return results
