"""Indeed RSS scraper — internships AI/LLM.

⚠️ STATUS (vérifié 2026-05-20) : l'endpoint RSS /rss?q= renvoie 404 (Indeed l'a
retiré), et l'endpoint HTML /jobs?q= renvoie un 403 "Security Check" (Cloudflare).

Pour récupérer des stages Indeed il faut :
  - soit la Indeed Publisher API (gratuite mais nécessite une clé : INDEED_API_KEY)
  - soit un proxy résidentiel + Playwright
  - soit ScraperAPI / ZenRows en proxy frontal

Cette source reste un stub qui renvoie [] sauf si INDEED_API_KEY est configurée.
"""

import os

import re
import time
from datetime import datetime, timezone
from urllib.parse import quote
from xml.etree import ElementTree as ET

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; troy-pain-hunter/1.0)"}
RESULTS_PER_KEYWORD = 8


def _parse_pubdate(s: str) -> str | None:
    if not s:
        return None
    try:
        # RFC 822 → ISO
        dt = datetime.strptime(s, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.replace(tzinfo=timezone.utc).isoformat()
    except Exception:
        return None


def fetch_indeed_rss(keywords: list[str]) -> list[dict]:
    if not os.getenv("INDEED_API_KEY"):
        return []  # Stub : voir docstring du module pour activer.
    results: list[dict] = []
    for kw in keywords:
        q = quote(kw)
        for domain, country in (("fr.indeed.com", "FR"), ("www.indeed.com", "US")):
            url = f"https://{domain}/rss?q={q}"
            try:
                r = requests.get(url, headers=HEADERS, timeout=12)
                if r.status_code != 200 or not r.text.strip().startswith("<?xml"):
                    continue
                root = ET.fromstring(r.text)
                channel = root.find("channel")
                if channel is None:
                    continue
                for item in channel.findall("item")[:RESULTS_PER_KEYWORD]:
                    title = (item.findtext("title") or "").strip()
                    link = (item.findtext("link") or "").strip()
                    pub = _parse_pubdate(item.findtext("pubDate") or "")
                    description = (item.findtext("description") or "").strip()
                    description = re.sub(r"<[^>]+>", " ", description)[:400]
                    if not title or not link:
                        continue
                    results.append({
                        "source": f"indeed-{country.lower()}",
                        "url": link,
                        "text": f"{title} — {description}",
                        "score": 0,
                        "lang": "fr" if country == "FR" else "en",
                        "published_at": pub,
                    })
                time.sleep(1)
            except Exception:
                continue
    return results
