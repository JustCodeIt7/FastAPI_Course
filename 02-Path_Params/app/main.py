from fastapi import FastAPI, Path, Query, HTTPException
from enum import Enum
from typing import Optional, List

from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel, Field
from starlette.responses import HTMLResponse
import os

# Initialize FastAPI app with metadata
app = FastAPI(
    title="FastAPI Path, Query, and Predefined Parameters",
    description="Comprehensive demo for YouTube tutorial",
    version="1.0.0",
)


# Enum class for predefined video categories
class VideoCategory(str, Enum):
    TECH = "tech"
    GAMING = "gaming"
    MUSIC = "music"


# Pydantic model for video data validation and serialization
class Video(BaseModel):
    id: int
    title: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)
    category: VideoCategory
    views: int = Field(..., ge=0)
    likes: int = Field(..., ge=0)


# In-memory database to store video data
videos = {
    1: Video(
        id=1,
        title="FastAPI Tutorial",
        description="Learn FastAPI basics",
        category=VideoCategory.TECH,
        views=1500,
        likes=200,
    ),
    2: Video(
        id=2,
        title="Python for Beginners",
        description="Introduction to Python",
        category=VideoCategory.TECH,
        views=1200,
        likes=150,
    ),
    3: Video(
        id=3,
        title="Gaming Setup Tour",
        description="My gaming setup",
        category=VideoCategory.GAMING,
        views=800,
        likes=100,
    ),
    4: Video(
        id=4,
        title="Guitar Lesson 1",
        description="Beginner guitar lesson",
        category=VideoCategory.MUSIC,
        views=2000,
        likes=300,
    ),
}


########### Initialize Data ##############
@app.get("/", response_class=HTMLResponse)
async def root():
    with open("index.html", "r") as f:
        # Read and return the contents of index.html as an HTML response
        return HTMLResponse(content=f.read(), status_code=200)  # http://0.0.0.0:8000/


# display up to 10 videos
@app.get("/videos/", response_model=List[Video])
async def get_videos():
    """
    :return: A list of videos with a default limit of 10.
    """
    # http://0.0.0.0:8000/videos/
    return list(videos.values())[:10]


@app.get("/videos/{video_id}")
async def get_video(video_id: int = Path(..., gt=0, description="ID of the video")):
    """
    Retrieve a video by its ID.

    :param video_id: The ID of the video to retrieve.
    :return: The video object if found.
    :raises HTTPException: If the video with the given ID is not found.
    """
    if video_id not in videos:
        # Raise a 404 error if the video ID does not exist
        raise HTTPException(status_code=404, detail="Video not found")
    return videos[video_id]  # http://0.0.0.0:8000/videos/1


@app.get("/categories/{category}/videos")
async def get_videos_by_category(
    category: VideoCategory,
    limit: int = Query(
        10, gt=0, le=100, description="Maximum number of videos to return"
    ),
    skip: int = Query(0, ge=0, description="Number of videos to skip"),
):
    """
    Retrieve videos filtered by category with pagination.

    :param category: The category of videos to filter by (tech, gaming, music).
    :param limit: Maximum number of videos to return (default is 10, max 100).
    :param skip: Number of videos to skip for pagination (default is 0).
    :return: A list of videos matching the category and pagination parameters.
    """
    # Filter videos based on the specified category
    filtered_videos = [video for video in videos.values() if video.category == category]
    # Return the sliced list of videos based on skip and limit
    # http://0.0.0.0:8000/categories/tech/videos
    return filtered_videos[skip : skip + limit]


@app.get("/users/{user_id}/videos/{video_id}/stats")
async def get_video_stats(
    user_id: int = Path(..., gt=0, description="ID of the user"),
    video_id: int = Path(..., gt=0, description="ID of the video"),
    watched: bool = Query(False, description="Whether the video was watched"),
):
    """
    Retrieve statistics for a specific video and user.

    :param user_id: The ID of the user requesting the stats.
    :param video_id: The ID of the video for which to retrieve stats.
    :param watched: Indicates if the user has watched the video (default is False).
    :return: A dictionary containing user ID, video ID, watched status, and video data.
    :raises HTTPException: If the video with the given ID is not found.
    """
    if video_id not in videos:
        # Raise a 404 error if the video ID does not exist
        raise HTTPException(status_code=404, detail="Video not found")
    # http://0.0.0.0:8000/users/1/videos/1/stats
    return {
        "user_id": user_id,
        "video_id": video_id,
        "watched": watched,
        "video_data": videos[video_id],
    }


@app.post("/videos/")
async def create_video(video: Video):
    """
    Create a new video entry.

    :param video: The video data to create, adhering to the Video model.
    :return: A confirmation message with the newly created video ID.
    """
    # Determine the next available video ID
    next_id = max(videos.keys()) + 1
    # Add the new video to the in-memory database
    videos[next_id] = video
    # http://0.0.0.0:8000/videos/
    return {"message": "Video created successfully", "video_id": next_id}


if __name__ == "__main__":
    # Run the application using Uvicorn for development purposes
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
