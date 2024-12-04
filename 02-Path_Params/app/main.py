from fastapi import FastAPI, Path, Query, HTTPException
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from starlette.responses import HTMLResponse
import os
app = FastAPI(
    title="FastAPI Path, Query, and Predefined Parameters",
    description="Comprehensive demo for YouTube tutorial",
    version="1.0.0"
)

# Enums for predefined values
class VideoCategory(str, Enum):
    TECH = "tech"
    GAMING = "gaming"
    MUSIC = "music"


# Pydantic model for video data
class Video(BaseModel):
    id: int
    title: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    category: VideoCategory
    views: int = Field(..., ge=0)
    likes: int = Field(..., ge=0)


# Sample video data (in-memory database)
videos = {
    1: Video(id=1, title="FastAPI Tutorial", description="Learn FastAPI basics", category=VideoCategory.TECH, views=1500, likes=200),
    2: Video(id=2, title="Python for Beginners", description="Introduction to Python", category=VideoCategory.TECH, views=1200, likes=150),
    3: Video(id=3, title="Gaming Setup Tour", description="My gaming setup", category=VideoCategory.GAMING, views=800, likes=100),
    4: Video(id=4, title="Guitar Lesson 1", description="Beginner guitar lesson", category=VideoCategory.MUSIC, views=2000, likes=300),
}


@app.get("/", response_class=HTMLResponse)
async def root():
    # display index.html
    print("Starting")
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)



# Path parameter with validation
@app.get("/videos/{video_id}")
async def get_video(video_id: int = Path(..., gt=0, description="ID of the video")):
    if video_id not in videos:
        raise HTTPException(status_code=404, detail="Video not found")
    return videos[video_id]


# Predefined path values and query parameters (removed sorting)
@app.get("/categories/{category}/videos")
async def get_videos_by_category(
    category: VideoCategory,
    limit: int = Query(10, gt=0, le=100, description="Maximum number of videos to return"),
    skip: int = Query(0, ge=0, description="Number of videos to skip")
):
    filtered_videos = [video for video in videos.values() if video.category == category]
    return filtered_videos[skip : skip + limit]  # Corrected slicing


# Multiple path parameters and query parameters
@app.get("/users/{user_id}/videos/{video_id}/stats")
async def get_video_stats(
    user_id: int = Path(..., gt=0, description="ID of the user"),
    video_id: int = Path(..., gt=0, description="ID of the video"),
    watched: bool = Query(False, description="Whether the video was watched")
):
    if video_id not in videos:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"user_id": user_id, "video_id": video_id, "watched": watched, "video_data": videos[video_id]}


# Request body and path parameters
@app.post("/videos/")
async def create_video(video: Video):
    next_id = max(videos.keys()) + 1
    videos[next_id] = video
    return {"message": "Video created successfully", "video_id": next_id}


# Created/Modified files during execution:
# main.py
# Created/Modified files during execution:
# main.py
if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn
    uvicorn.run('main:app', host="0.0.0.0", port=8001, log_level="debug", reload=True)