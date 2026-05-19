import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

SL_PATH = os.path.expanduser("~/mchanpeng/git/sl")
sys.path.insert(0, SL_PATH)

from sources.reddit import fetch_reddit
from sources.google import fetch_google
from sources.twitter import fetch_twitter
from sources.facebook import fetch_facebook
from memory.troy_memory import TroyMemory

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

VALID_SCOPES = ("annoying", "saas", "physical", "freelance")


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

        scope_results.extend(fetch_reddit(keywords))
        scope_results.extend(fetch_google(keywords))
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
