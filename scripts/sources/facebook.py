import time
import requests

FB_SEARCH_URL = "https://graph.facebook.com/v18.0/search"
RESULTS_PER_KEYWORD = 5


def fetch_facebook(keywords: list[str], access_token: str | None) -> list[dict]:
    if not access_token:
        return []

    results = []

    for keyword in keywords:
        try:
            response = requests.get(
                FB_SEARCH_URL,
                params={
                    "q": keyword,
                    "type": "post",
                    "limit": RESULTS_PER_KEYWORD,
                    "access_token": access_token,
                    "fields": "id,message,story",
                },
                timeout=10,
            )
            data = response.json()
            for post in data.get("data", []):
                text = post.get("message") or post.get("story") or ""
                if not text.strip():
                    continue
                results.append({
                    "source": "facebook",
                    "url": f"https://facebook.com/{post.get('id', '')}",
                    "text": text[:500],
                    "score": 0,
                    "lang": "fr",
                })
            time.sleep(1)
        except Exception:
            continue

    return results
