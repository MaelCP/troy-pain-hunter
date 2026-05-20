"""HelloWork (ex-RegionsJob) — FR jobs incl. stages.

HelloWork sert toujours du HTML SSR-friendly et expose un RSS sur les
recherches : https://www.hellowork.com/fr-fr/recherche.html?q=stage+LLM&rss=1
"""

import re
import time
from datetime import datetime, timezone
from urllib.parse import quote
from xml.etree import ElementTree as ET

import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; troy-pain-hunter/1.0)"}
RESULTS_PER_KEYWORD = 6


def _parse_pub(s: str) -> str | None:
    if not s:
        return None
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
        try:
            return datetime.strptime(s, fmt).astimezone(timezone.utc).isoformat()
        except Exception:
            continue
    return None


def fetch_hellowork(keywords: list[str]) -> list[dict]:
    results: list[dict] = []
    for kw in keywords:
        q = quote(kw)
        url = (
            "https://www.hellowork.com/fr-fr/emploi/recherche.html"
            f"?k={q}&t=Stage"
        )
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                continue
            # Cards : <a class="ad-result-card" href="/fr-fr/emplois/XXX.html">
            anchors = re.findall(
                r'<a[^>]+class="[^"]*ad-result-card[^"]*"[^>]+href="([^"]+)"[^>]*>([\s\S]{0,500}?)</a>',
                r.text,
            )
            if not anchors:
                # fallback : generic job links
                anchors = re.findall(
                    r'<a[^>]+href="(/fr-fr/emplois/[^"]+\.html)"[^>]*>([\s\S]{0,500}?)</a>',
                    r.text,
                )
            for href, inner in anchors[:RESULTS_PER_KEYWORD]:
                title_match = re.search(r"<h\d[^>]*>(.*?)</h\d>", inner, re.S)
                title = (
                    re.sub(r"<[^>]+>", " ", title_match.group(1)).strip()
                    if title_match else
                    re.sub(r"<[^>]+>", " ", inner).strip()[:120]
                )
                title = re.sub(r"\s+", " ", title)
                if not title:
                    continue
                full_url = (
                    "https://www.hellowork.com" + href
                    if href.startswith("/") else href
                )
                results.append({
                    "source": "hellowork",
                    "url": full_url.split("?")[0],
                    "text": title[:400],
                    "score": 0,
                    "lang": "fr",
                    "published_at": None,
                })
            time.sleep(2)
        except Exception:
            continue
    return results
