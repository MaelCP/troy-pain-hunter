"""Welcome to the Jungle scraper — internships.

⚠️ STATUS (vérifié 2026-05-20) : leur site est devenu une SPA pure (Next.js
client-rendered). Le HTML servi en SSR ne contient plus de __NEXT_DATA__
exploitable. Les credentials Algolia ne sont plus exposés dans le HTML.

Pour récupérer des stages WTTJ il faut :
  - soit un Playwright headless (out of scope ici)
  - soit récupérer dynamiquement la clé Algolia depuis leur bundle JS
    (`/static/chunks/main-*.js`) à chaque exécution — fragile, à coder
  - soit demander l'accès à leur API officielle B2B

Cette source reste un stub qui renvoie [] sauf si WTTJ_ALGOLIA_KEY est configurée.
"""

import os

import json
import re
import time
from datetime import datetime, timezone
from urllib.parse import quote

import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}
RESULTS_PER_KEYWORD = 6


def fetch_wttj(keywords: list[str]) -> list[dict]:
    """Scrape WTTJ via leur page HTML publique de search (fallback robuste)."""
    if not os.getenv("WTTJ_ALGOLIA_KEY"):
        return []  # Stub : voir docstring du module pour activer.
    results: list[dict] = []
    for kw in keywords:
        q = quote(kw)
        url = f"https://www.welcometothejungle.com/fr/jobs?query={q}&contract_type[]=internship"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code != 200:
                continue
            # WTTJ embeds preloaded results in a <script id="__NEXT_DATA__">
            m = re.search(
                r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                r.text,
                re.S,
            )
            if not m:
                continue
            try:
                payload = json.loads(m.group(1))
            except Exception:
                continue
            # Best-effort path through Algolia result structure
            hits = _walk_for_hits(payload)
            for h in hits[:RESULTS_PER_KEYWORD]:
                name = h.get("name") or h.get("title") or ""
                slug = h.get("slug") or ""
                company = (h.get("organization") or {}).get("name", "")
                published = h.get("published_at") or h.get("created_at")
                pub_iso = None
                if published:
                    try:
                        pub_iso = datetime.fromisoformat(
                            published.replace("Z", "+00:00")
                        ).astimezone(timezone.utc).isoformat()
                    except Exception:
                        pub_iso = None
                url_job = (
                    f"https://www.welcometothejungle.com/fr/companies/"
                    f"{(h.get('organization') or {}).get('slug', '')}/jobs/{slug}"
                    if slug else None
                )
                if not name or not url_job:
                    continue
                results.append({
                    "source": "wttj",
                    "url": url_job,
                    "text": f"{name} — {company}",
                    "score": 0,
                    "lang": "fr",
                    "published_at": pub_iso,
                })
            time.sleep(2)
        except Exception:
            continue
    return results


def _walk_for_hits(obj, out=None, depth=0):
    """Find any `hits` array of Algolia-shaped job objects in the JSON tree."""
    if out is None:
        out = []
    if depth > 15:
        return out
    if isinstance(obj, dict):
        if isinstance(obj.get("hits"), list) and obj["hits"] and isinstance(obj["hits"][0], dict):
            sample = obj["hits"][0]
            if any(k in sample for k in ("slug", "name", "organization")):
                out.extend(obj["hits"])
        for v in obj.values():
            _walk_for_hits(v, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj:
            _walk_for_hits(v, out, depth + 1)
    return out
