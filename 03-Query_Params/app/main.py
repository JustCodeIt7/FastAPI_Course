from fastapi import FastAPI, Path, Query, HTTPException
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field
from starlette.responses import HTMLResponse
import os

app = FastAPI(
    title="FastAPI Path, Query, and Predefined Parameters",
    description="Comprehensive demo for YouTube tutorial",
    version="1.0.0",
)


@app.get("/", response_class=HTMLResponse)
async def root():
    # display index.html
    print("Starting")
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, log_level="debug", reload=True)
