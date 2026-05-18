import json
import os
import sys
from dotenv import load_dotenv

from keywords import ALL_KEYWORDS
from sources.reddit import fetch_reddit
from sources.google import fetch_google
from sources.twitter import fetch_twitter
from sources.facebook import fetch_facebook

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


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


def run() -> str:
    errors = []
    all_results = []
    sources_used = []

    # Reddit (no key required)
    reddit_results = fetch_reddit(ALL_KEYWORDS)
    all_results.extend(reddit_results)
    sources_used.append("reddit")

    # Google (no key required)
    google_results = fetch_google(ALL_KEYWORDS)
    all_results.extend(google_results)
    sources_used.append("google")

    # Twitter (key required)
    twitter_token = os.getenv("TWITTER_BEARER_TOKEN")
    if not twitter_token:
        errors.append("twitter skipped: TWITTER_BEARER_TOKEN manquant dans .env")
    else:
        twitter_results = fetch_twitter(ALL_KEYWORDS, bearer_token=twitter_token)
        all_results.extend(twitter_results)
        sources_used.append("twitter")

    # Facebook (key required)
    fb_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    if not fb_token:
        errors.append("facebook skipped: FACEBOOK_ACCESS_TOKEN manquant dans .env")
    else:
        fb_results = fetch_facebook(ALL_KEYWORDS, access_token=fb_token)
        all_results.extend(fb_results)
        sources_used.append("facebook")

    deduped = deduplicate(all_results)
    sorted_results = aggregate(deduped)

    return json.dumps({
        "results": sorted_results,
        "errors": errors,
        "sources_used": sources_used,
        "total": len(sorted_results),
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print(run())
