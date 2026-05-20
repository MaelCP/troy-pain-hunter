"""Google site: search — contourne les blocs Indeed/WTTJ.

Google indexe Indeed et WTTJ malgré leur anti-scrape direct. On utilise
le custom search ou DuckDuckGo HTML.
"""

import re
import time
from urllib.parse import quote, urlparse

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html",
}
TARGETS = [
    ("fr.indeed.com", "indeed-fr", "fr"),
    ("www.indeed.com", "indeed-us", "en"),
    ("welcometothejungle.com", "wttj", "fr"),
]
RESULTS_PER_TARGET_KW = 5


def _ddg_search(query: str) -> list[tuple[str, str]]:
    """DuckDuckGo HTML search (no auth needed)."""
    try:
        r = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=HEADERS,
            timeout=15,
        )
        if r.status_code != 200:
            return []
        # Parse result anchors
        pairs = re.findall(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            r.text,
            re.S,
        )
        out = []
        for href, title in pairs:
            title_clean = re.sub(r"<[^>]+>", "", title).strip()
            # DDG sometimes wraps URLs in /l/?uddg=
            m = re.search(r"uddg=([^&]+)", href)
            if m:
                from urllib.parse import unquote
                href = unquote(m.group(1))
            out.append((href, title_clean))
        return out
    except Exception:
        return []


def fetch_google_jobs(keywords: list[str]) -> list[dict]:
    """Recherche stages IA/LLM via DDG site: pour contourner anti-scrape."""
    results: list[dict] = []
    seen: set[str] = set()
    for kw in keywords:
        for site, label, lang in TARGETS:
            query = f"site:{site} {kw}"
            pairs = _ddg_search(query)
            time.sleep(2)
            for href, title in pairs[:RESULTS_PER_TARGET_KW]:
                if not href or href in seen:
                    continue
                seen.add(href)
                parsed = urlparse(href)
                if site not in parsed.netloc:
                    continue
                # Filtrer les pages génériques (search, /jobs sans slug, etc.)
                if parsed.path in ("", "/", "/jobs", "/fr/jobs", "/rss"):
                    continue
                if not title:
                    title = href
                results.append({
                    "source": label,
                    "url": href.split("?")[0],
                    "text": title[:400],
                    "score": 0,
                    "lang": lang,
                    "published_at": None,
                })
    return results
