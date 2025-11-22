# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from yt_service import fetch_gl_videos

app = FastAPI(title="GL Video API")

# Allow requests from Flutter dev (adjust origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "GL Video API - use /gl-videos"}

@app.get("/gl-videos")
def gl_videos(category: str = None, page: int = 1, limit: int = 20):
    """
    Get GL videos with optional category filtering and pagination.
    
    Args:
        category: Optional category filter (Thai, Korean, Chinese, Japanese, Asian, International)
        page: Page number (default: 1)
        limit: Number of videos per page (default: 20, max: 50)
    """
    # Ensure API key present
    if not os.getenv("YOUTUBE_API_KEY"):
        raise HTTPException(status_code=500, detail="YOUTUBE_API_KEY not set in environment")
    
    # Validate inputs
    if page < 1:
        page = 1
    if limit < 1:
        limit = 20
    if limit > 50:
        limit = 50
    
    try:
        videos, total_count = fetch_gl_videos(
            prioritize_shorts=True,
            category=category,
            page=page,
            limit=limit
        )
        return {
            "videos": videos,
            "count": len(videos),
            "total": total_count,
            "page": page,
            "limit": limit,
            "hasMore": (page * limit) < total_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

