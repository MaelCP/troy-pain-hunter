"""Free-Work — FR tech jobs/stages, scrapable directement.

URL pattern: https://www.free-work.com/fr/tech-it/jobs?contracts=internship&query=<kw>
Liens d'annonces : /fr/tech-it/<role-slug>/job-mission/<slug>
"""

import re
import time
from urllib.parse import quote

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html",
}
RESULTS_PER_KEYWORD = 8


def fetch_freework(keywords: list[str]) -> list[dict]:
    results: list[dict] = []
    seen: set[str] = set()
    for kw in keywords:
        q = quote(kw)
        url = (
            "https://www.free-work.com/fr/tech-it/jobs"
            f"?contracts=internship,apprenticeship&query={q}"
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            html = r.text
            # Each card link looks like: href="/fr/tech-it/<role>/job-mission/<slug>"
            # Title appears in the surrounding HTML — try to grab <a ...>(title)</a>
            for m in re.finditer(
                r'href="(/fr/tech-it/[^"]+/job-mission/[^"]+)"[^>]*>([\s\S]{0,400}?)</a>',
                html,
            ):
                href, inner = m.group(1), m.group(2)
                if href in seen:
                    continue
                seen.add(href)
                title = re.sub(r"<[^>]+>", " ", inner).strip()
                title = re.sub(r"\s+", " ", title)[:200]
                if not title:
                    continue
                results.append({
                    "source": "free-work",
                    "url": "https://www.free-work.com" + href,
                    "text": title,
                    "score": 0,
                    "lang": "fr",
                    "published_at": None,
                })
                if len(results) >= RESULTS_PER_KEYWORD * len(keywords):
                    break
            time.sleep(2)
        except Exception:
            continue
    return results
