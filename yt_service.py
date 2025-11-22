# yt_service.py
import requests
from typing import List, Dict
import os

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
API_KEY = os.getenv("YOUTUBE_API_KEY")

SHORTS_KEYWORDS = [
    "lesbian short", "gl short", "wlw short", "girls love short",
    "yuri short", "sapphic short", "lesbian edits short"
]

NORMAL_KEYWORDS = [
    "lesbian scenes", "gl series scenes", "wlw scenes", "yuri kiss scene",
    "girls love movie", "sapphic movie clip"
]

def search_youtube(keyword: str, is_short: bool = True, max_results: int = 8) -> List[Dict]:
    params = {
        "part": "snippet",
        "q": keyword,
        "key": API_KEY,
        "maxResults": max_results,
        "type": "video"
    }
    if is_short:
        params["videoDuration"] = "short"

    resp = requests.get(YOUTUBE_SEARCH_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("items", [])

    results = []
    for it in items:
        vid_id = it["id"].get("videoId")
        if not vid_id:
            continue
        snippet = it["snippet"]
        thumb = snippet.get("thumbnails", {}).get("high", {}).get("url") or snippet.get("thumbnails", {}).get("default", {}).get("url")
        results.append({
            "title": snippet.get("title"),
            "channelTitle": snippet.get("channelTitle"),
            "thumbnail": thumb,
            "videoId": vid_id,
            "publishedAt": snippet.get("publishedAt"),
            "isShort": is_short
        })
    return results

def fetch_gl_videos(prioritize_shorts: bool = True) -> List[Dict]:
    results = []
    # First: Shorts (primary)
    for kw in (SHORTS_KEYWORDS if prioritize_shorts else NORMAL_KEYWORDS):
        try:
            results.extend(search_youtube(kw, is_short=True))
        except Exception as e:
            # non-fatal; continue
            print(f"Error searching shorts for {kw}: {e}")
    # Second: Normal videos (secondary)
    for kw in NORMAL_KEYWORDS:
        try:
            results.extend(search_youtube(kw, is_short=False))
        except Exception as e:
            print(f"Error searching normal for {kw}: {e}")
    # Optional: deduplicate by videoId (keep first occurrence)
    seen = set()
    unique = []
    for r in results:
        if r["videoId"] in seen:
            continue
        seen.add(r["videoId"])
        unique.append(r)
    return unique

