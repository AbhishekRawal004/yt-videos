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
def gl_videos():
    # Ensure API key present
    if not os.getenv("YOUTUBE_API_KEY"):
        raise HTTPException(status_code=500, detail="YOUTUBE_API_KEY not set in environment")
    try:
        videos = fetch_gl_videos(prioritize_shorts=True)
        return {"videos": videos, "count": len(videos)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

