import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

SL_PATH = "/Users/satoshi/Projets/bizness/troy-memory-engine"
sys.path.insert(0, SL_PATH)
sys.path.insert(0, os.path.dirname(__file__))

from sources.reddit import fetch_reddit
from sources.google import fetch_google
from sources.twitter import fetch_twitter
from sources.facebook import fetch_facebook
from sources.hackernews import fetch_hackernews
from sources.indiehackers import fetch_indiehackers
from sources.github import fetch_github
from sources.stackexchange import fetch_stackexchange
from sources.devto import fetch_devto
from sources.lobsters import fetch_lobsters
from sources.trustpilot import fetch_trustpilot
from sources.medium import fetch_medium
from sources.newsletters import fetch_newsletters
from sources.indeed_rss import fetch_indeed_rss
from sources.wttj import fetch_wttj
from sources.linkedin_jobs import fetch_linkedin_jobs
from sources.google_jobs import fetch_google_jobs
from sources.hellowork import fetch_hellowork
from sources.wellfound import fetch_wellfound
from sources.freework import fetch_freework
from memory.troy_memory import TroyMemory

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

VALID_SCOPES = ("annoying", "saas", "physical", "freelance", "internships")


def resolve_scopes(requested: list[str]) -> list[str]:
    if requested == ["all"]:
        return list(VALID_SCOPES)
    invalid = [s for s in requested if s not in VALID_SCOPES]
    if invalid:
        raise ValueError(
            f"Unknown scope: {', '.join(invalid)}. Valid: {', '.join(VALID_SCOPES)}, all"
        )
    return requested


def _load_keywords(scope: str) -> list[str]:
    if scope == "annoying":
        from scopes.annoying import KEYWORDS_EN, KEYWORDS_FR
    elif scope == "saas":
        from scopes.saas import KEYWORDS_EN, KEYWORDS_FR
    elif scope == "physical":
        from scopes.physical import KEYWORDS_EN, KEYWORDS_FR
    elif scope == "freelance":
        from scopes.freelance import KEYWORDS_EN, KEYWORDS_FR
    elif scope == "internships":
        from scopes.internships import KEYWORDS_EN, KEYWORDS_FR
    return KEYWORDS_EN + KEYWORDS_FR


def deduplicate(results: list[dict]) -> list[dict]:
    seen_urls = set()
    unique = []
    for r in results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique.append(r)
    return unique


def aggregate(results: list[dict]) -> list[dict]:
    return sorted(results, key=lambda r: r["score"], reverse=True)


def run(scopes: list[str] | None = None) -> str:
    scopes = resolve_scopes(scopes or ["all"])
    errors = []
    all_results = []
    by_scope: dict[str, int] = {}
    new_results = 0
    already_seen = 0
    now = datetime.utcnow().isoformat()

    twitter_token = os.getenv("TWITTER_BEARER_TOKEN")
    fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    if not twitter_token:
        errors.append("twitter skipped: TWITTER_BEARER_TOKEN manquant dans .env")
    if not fb_token:
        errors.append("facebook skipped: FACEBOOK_ACCESS_TOKEN manquant dans .env")

    memory = TroyMemory()

    for scope in scopes:
        keywords = _load_keywords(scope)
        scope_results = []

        if scope == "internships":
            # Pour stages : sources jobs only (signal différent des pains)
            # Sources qui marchent direct (testées 2026-05-20) :
            scope_results.extend(fetch_linkedin_jobs(keywords))
            scope_results.extend(fetch_freework(keywords))
            # Sources qui nécessitent une clé API/proxy (stubs) :
            scope_results.extend(fetch_indeed_rss(keywords))   # → INDEED_API_KEY
            scope_results.extend(fetch_wttj(keywords))         # → WTTJ_ALGOLIA_KEY
            scope_results.extend(fetch_hellowork(keywords))    # SPA, à recoder via Playwright
            scope_results.extend(fetch_wellfound(keywords))    # DDG bloque, à recoder via SerpAPI
            scope_results.extend(fetch_google_jobs(keywords))  # DDG bloque, à recoder via SerpAPI
        else:
            scope_results.extend(fetch_reddit(keywords))
            scope_results.extend(fetch_google(keywords))
            scope_results.extend(fetch_hackernews(keywords))
            scope_results.extend(fetch_indiehackers(keywords))
            scope_results.extend(fetch_github(keywords))
            scope_results.extend(fetch_stackexchange(keywords))
            scope_results.extend(fetch_devto(keywords))
            scope_results.extend(fetch_lobsters(keywords))
            scope_results.extend(fetch_trustpilot(keywords))
            scope_results.extend(fetch_medium(keywords))
            scope_results.extend(fetch_newsletters(keywords))
            if twitter_token:
                scope_results.extend(fetch_twitter(keywords, bearer_token=twitter_token))
            if fb_token:
                scope_results.extend(fetch_facebook(keywords, access_token=fb_token))

        scope_new = []
        for r in scope_results:
            if memory.seen_url(r["url"]):
                already_seen += 1
            else:
                r["scope"] = scope
                r["scraped_at"] = now
                scope_new.append(r)

        deduped = deduplicate(scope_new)
        inserted = memory.save_results(deduped)
        new_results += inserted
        by_scope[scope] = len(deduped)
        all_results.extend(deduped)

    sorted_results = aggregate(deduplicate(all_results))

    return json.dumps({
        "results": sorted_results,
        "by_scope": by_scope,
        "new_results": new_results,
        "already_seen": already_seen,
        "errors": errors,
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", nargs="+", default=["all"])
    args = parser.parse_args()
    print(run(scopes=args.scope))
