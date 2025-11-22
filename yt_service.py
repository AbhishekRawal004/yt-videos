# yt_service.py
import requests
from typing import List, Dict, Optional, Tuple
import os

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
API_KEY = os.getenv("YOUTUBE_API_KEY")

# Category-specific keywords for lesbian content
CATEGORY_KEYWORDS = {
    "Thai": [
        "lesbian thai short", "gl thai short", "wlw thai short", "yuri thai short",
        "lesbian thai", "gl thai series", "thai girls love"
    ],
    "Korean": [
        "lesbian korean short", "gl korean short", "wlw korean short", "yuri korean short",
        "lesbian korean", "gl korean drama", "korean girls love"
    ],
    "Chinese": [
        "lesbian chinese short", "gl chinese short", "wlw chinese short", "yuri chinese short",
        "lesbian chinese", "gl chinese drama", "chinese girls love"
    ],
    "Japanese": [
        "lesbian japanese short", "gl japanese short", "wlw japanese short", "yuri japanese short",
        "lesbian japanese", "gl japanese anime", "japanese girls love"
    ],
    "Asian": [
        "lesbian asian short", "gl asian short", "wlw asian short", "yuri asian short",
        "lesbian asian", "gl asian drama", "asian girls love"
    ],
    "International": [
        "lesbian short", "gl short", "wlw short", "girls love short",
        "yuri short", "sapphic short", "lesbian edits short"
    ]
}

SHORTS_KEYWORDS = [
    "lesbian short", "gl short", "wlw short", "girls love short",
    "yuri short", "sapphic short", "lesbian edits short"
]

NORMAL_KEYWORDS = [
    "lesbian scenes", "gl series scenes", "wlw scenes", "yuri kiss scene",
    "girls love movie", "sapphic movie clip"
]

def search_youtube(keyword: str, is_short: bool = True, max_results: int = 8, page_token: Optional[str] = None) -> Tuple[List[Dict], Optional[str]]:
    """
    Search YouTube videos with pagination support.
    Returns: (results_list, next_page_token)
    """
    params = {
        "part": "snippet",
        "q": keyword,
        "key": API_KEY,
        "maxResults": max_results,
        "type": "video"
    }
    if is_short:
        params["videoDuration"] = "short"
    if page_token:
        params["pageToken"] = page_token

    resp = requests.get(YOUTUBE_SEARCH_URL, params=params)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("items", [])
    next_page_token = data.get("nextPageToken")

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
    return results, next_page_token

def fetch_gl_videos(
    prioritize_shorts: bool = True,
    category: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> Tuple[List[Dict], int]:
    """
    Fetch GL videos with category filtering and pagination.
    Returns: (videos_list, total_count)
    """
    # Select keywords based on category
    if category and category in CATEGORY_KEYWORDS:
        keywords_to_use = CATEGORY_KEYWORDS[category]
    else:
        keywords_to_use = SHORTS_KEYWORDS if prioritize_shorts else NORMAL_KEYWORDS
    
    all_results = []
    seen = set()
    
    # Calculate how many results we need per keyword to get enough total results
    # We want at least `limit` results, so we'll search multiple keywords
    results_per_keyword = max(limit // len(keywords_to_use), 5)
    
    # First: Shorts (primary) - get more results
    for kw in keywords_to_use:
        try:
            # For pagination, we'll use multiple page tokens if needed
            page_token = None
            keyword_results = []
            
            # Fetch multiple pages if needed to get enough results
            for _ in range(2):  # Try 2 pages per keyword
                batch_results, next_token = search_youtube(
                    kw, 
                    is_short=True, 
                    max_results=min(results_per_keyword, 50),
                    page_token=page_token
                )
                
                for r in batch_results:
                    if r["videoId"] not in seen:
                        seen.add(r["videoId"])
                        keyword_results.append(r)
                
                if not next_token or len(keyword_results) >= results_per_keyword:
                    break
                page_token = next_token
            
            all_results.extend(keyword_results)
        except Exception as e:
            print(f"Error searching shorts for {kw}: {e}")
    
    # Second: Normal videos (secondary) - only if we don't have enough shorts
    if len(all_results) < limit:
        for kw in (NORMAL_KEYWORDS if not category else keywords_to_use):
            try:
                batch_results, _ = search_youtube(kw, is_short=False, max_results=5)
                for r in batch_results:
                    if r["videoId"] not in seen:
                        seen.add(r["videoId"])
                        all_results.append(r)
                        if len(all_results) >= limit * 2:  # Get extra for pagination
                            break
                if len(all_results) >= limit * 2:
                    break
            except Exception as e:
                print(f"Error searching normal for {kw}: {e}")
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_results = all_results[start_idx:end_idx]
    
    return paginated_results, len(all_results)

