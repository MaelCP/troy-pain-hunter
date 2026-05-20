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

# Registry of all sources. Keys are the names exposed via --sources / --skip-sources.
# `needs` lists env vars required for the source to run.
SOURCES_PAINS = {
    "reddit": {"fn": fetch_reddit, "needs": []},
    "google": {"fn": fetch_google, "needs": []},
    "hackernews": {"fn": fetch_hackernews, "needs": []},
    "indiehackers": {"fn": fetch_indiehackers, "needs": []},
    "github": {"fn": fetch_github, "needs": []},
    "stackexchange": {"fn": fetch_stackexchange, "needs": []},
    "devto": {"fn": fetch_devto, "needs": []},
    "lobsters": {"fn": fetch_lobsters, "needs": []},
    "trustpilot": {"fn": fetch_trustpilot, "needs": []},
    "medium": {"fn": fetch_medium, "needs": []},
    "newsletters": {"fn": fetch_newsletters, "needs": []},
    "twitter": {"fn": fetch_twitter, "needs": ["TWITTER_BEARER_TOKEN"]},
    "facebook": {"fn": fetch_facebook, "needs": ["FACEBOOK_ACCESS_TOKEN"]},
}

SOURCES_JOBS = {
    "linkedin_jobs": {"fn": fetch_linkedin_jobs, "needs": []},
    "freework": {"fn": fetch_freework, "needs": []},
    "indeed_rss": {"fn": fetch_indeed_rss, "needs": ["INDEED_API_KEY"]},
    "wttj": {"fn": fetch_wttj, "needs": ["WTTJ_ALGOLIA_KEY"]},
    "hellowork": {"fn": fetch_hellowork, "needs": []},
    "wellfound": {"fn": fetch_wellfound, "needs": []},
    "google_jobs": {"fn": fetch_google_jobs, "needs": []},
}


def _sources_for_scope(scope: str) -> dict:
    return SOURCES_JOBS if scope == "internships" else SOURCES_PAINS


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


def _select_sources(
    scope: str,
    only: list[str] | None,
    skip: list[str] | None,
) -> dict:
    """Filter the source registry for a given scope based on --sources / --skip-sources."""
    registry = _sources_for_scope(scope)
    if only:
        selected = {k: v for k, v in registry.items() if k in only}
    else:
        selected = dict(registry)
    if skip:
        selected = {k: v for k, v in selected.items() if k not in skip}
    return selected


def run(
    scopes: list[str] | None = None,
    only_sources: list[str] | None = None,
    skip_sources: list[str] | None = None,
    max_keywords: int | None = None,
    max_per_source: int | None = None,
) -> str:
    scopes = resolve_scopes(scopes or ["all"])
    errors = []
    all_results = []
    by_scope: dict[str, int] = {}
    by_source: dict[str, int] = {}
    new_results = 0
    already_seen = 0
    now = datetime.utcnow().isoformat()

    # Validate source filters early (catch typos)
    if only_sources:
        all_known = set(SOURCES_PAINS) | set(SOURCES_JOBS)
        unknown = [s for s in only_sources if s not in all_known]
        if unknown:
            raise ValueError(
                f"Unknown source(s): {', '.join(unknown)}. "
                f"Available: {', '.join(sorted(all_known))}"
            )

    memory = TroyMemory()

    for scope in scopes:
        keywords = _load_keywords(scope)
        if max_keywords is not None and max_keywords > 0:
            keywords = keywords[:max_keywords]

        sources = _select_sources(scope, only_sources, skip_sources)
        scope_results = []

        for name, meta in sources.items():
            # Check env-var prereqs
            missing = [v for v in meta["needs"] if not os.getenv(v)]
            if missing:
                errors.append(f"{name} skipped: {', '.join(missing)} manquant dans .env")
                continue
            try:
                if name == "twitter":
                    fetched = meta["fn"](keywords, bearer_token=os.getenv("TWITTER_BEARER_TOKEN"))
                elif name == "facebook":
                    fetched = meta["fn"](keywords, access_token=os.getenv("FACEBOOK_ACCESS_TOKEN"))
                else:
                    fetched = meta["fn"](keywords)
            except Exception as exc:
                errors.append(f"{name} failed: {exc}")
                continue
            if max_per_source is not None and max_per_source > 0:
                fetched = fetched[:max_per_source]
            by_source[name] = by_source.get(name, 0) + len(fetched)
            scope_results.extend(fetched)

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
        "by_source": by_source,
        "new_results": new_results,
        "already_seen": already_seen,
        "errors": errors,
    }, ensure_ascii=False, indent=2)


def _print_available_sources() -> None:
    print("Available sources:")
    print("  Pain sources (scopes: annoying, saas, physical, freelance):")
    for name, meta in sorted(SOURCES_PAINS.items()):
        flag = f"  (needs {','.join(meta['needs'])})" if meta["needs"] else ""
        print(f"    - {name}{flag}")
    print("  Job sources (scope: internships):")
    for name, meta in sorted(SOURCES_JOBS.items()):
        flag = f"  (needs {','.join(meta['needs'])})" if meta["needs"] else ""
        print(f"    - {name}{flag}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Troy Pain Hunter — scrape public frustrations to find SaaS opportunities."
    )
    parser.add_argument(
        "--scope",
        nargs="+",
        default=["all"],
        help=f"One or more of {', '.join(VALID_SCOPES)} or 'all'. Default: all.",
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=None,
        help="Whitelist : only run these sources (e.g. --sources reddit github). "
             "Use --list-sources to see all.",
    )
    parser.add_argument(
        "--skip-sources",
        nargs="+",
        default=None,
        help="Blacklist : skip these sources (e.g. --skip-sources medium trustpilot).",
    )
    parser.add_argument(
        "--max-keywords",
        type=int,
        default=None,
        help="Cap the number of keywords used per scope (smoke-test mode).",
    )
    parser.add_argument(
        "--max-per-source",
        type=int,
        default=None,
        help="Cap the number of results returned by each source (smoke-test mode).",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="Print the available source names and exit.",
    )
    args = parser.parse_args()

    if args.list_sources:
        _print_available_sources()
        sys.exit(0)

    print(run(
        scopes=args.scope,
        only_sources=args.sources,
        skip_sources=args.skip_sources,
        max_keywords=args.max_keywords,
        max_per_source=args.max_per_source,
    ))
