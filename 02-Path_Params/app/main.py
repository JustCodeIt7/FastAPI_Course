from fastapi import FastAPI, Path, HTTPException
from typing import Optional
from enum import Enum
from pydantic import BaseModel

app = FastAPI(
    title="YouTube FastAPI Tutorial",
    description="Learn about Path Parameters in FastAPI",
    version="1.0.0"
)

# Enum for video categories
class VideoCategory(str, Enum):
    TECH = "tech"
    GAMING = "gaming"
    MUSIC = "music"
    EDUCATION = "education"

# Pydantic model for Video
class Video(BaseModel):
    title: str
    description: str
    category: VideoCategory
    views: int
    likes: int

# Sample video database
videos_db = {
    1: Video(
        title="FastAPI Tutorial",
        description="Learn FastAPI Path Parameters",
        category=VideoCategory.TECH,
        views=1000,
        likes=100
    )
}

@app.get("/")
async def root():
    return {"message": "Welcome to YouTube API Tutorial"}

@app.get("/videos/{video_id}")
async def get_video(
    video_id: int = Path(
        ...,
        title="Video ID",
        description="The ID of the video you want to retrieve",
        ge=1
    )
):
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    return videos_db[video_id]

@app.get("/categories/{category}/videos")
async def get_videos_by_category(
    category: VideoCategory,
    skip: int = 0,
    limit: Optional[int] = 10
):
    videos = [
        video for video in videos_db.values()
        if video.category == category
    ]
    return videos[skip:skip + limit]

@app.get("/videos/{video_id}/stats")
async def get_video_stats(
    video_id: int = Path(
        ...,
        title="Video ID",
        description="The ID of the video to get statistics for",
        ge=1
    )
):
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")
    video = videos_db[video_id]
    return {
        "views": video.views,
        "likes": video.likes,
        "engagement_rate": round((video.likes / video.views) * 100, 2) if video.views > 0 else 0
    }

# Add a new video
@app.post("/videos/{video_id}")
async def create_video(
    video_id: int = Path(
        ...,
        title="Video ID",
        description="The ID for the new video",
        ge=1
    ),
    video: Video = None
):
    if video_id in videos_db:
        raise HTTPException(status_code=400, detail="Video ID already exists")
    videos_db[video_id] = video
    return video

# Created/Modified files during execution:
# main.py
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")