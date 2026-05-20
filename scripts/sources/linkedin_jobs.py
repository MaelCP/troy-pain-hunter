"""LinkedIn Jobs (guest endpoint).

L'endpoint `jobs-guest/jobs/api/seeMoreJobPostings/search` ne nécessite pas
de session — il renvoie du HTML fragmentaire qu'on parse au plus simple.
Très anti-scrape : on bornera à 1 page par keyword + sleep.
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


def fetch_linkedin_jobs(keywords: list[str]) -> list[dict]:
    results: list[dict] = []
    for kw in keywords:
        q = quote(kw)
        for geo, lang in (("France", "fr"), ("United%20States", "en")):
            url = (
                "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
                f"?keywords={q}&location={geo}&f_JT=I"  # f_JT=I = Internship
            )
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                if r.status_code != 200:
                    continue
                html = r.text
                cards = re.findall(
                    r'<li[^>]*>.*?<a class="base-card__full-link[^"]*"[^>]*href="([^"]+)"[^>]*>.*?'
                    r'<h3[^>]*>(.*?)</h3>.*?'
                    r'<h4[^>]*>.*?<a[^>]*>(.*?)</a>',
                    html,
                    re.S,
                )
                for href, title, company in cards[:RESULTS_PER_KEYWORD]:
                    title_clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", title)).strip()
                    company_clean = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", company)).strip()
                    if not title_clean:
                        continue
                    results.append({
                        "source": f"linkedin-{lang}",
                        "url": href.split("?")[0],
                        "text": f"{title_clean} — {company_clean}",
                        "score": 0,
                        "lang": lang,
                        "published_at": None,
                    })
                time.sleep(3)
            except Exception:
                continue
    return results
