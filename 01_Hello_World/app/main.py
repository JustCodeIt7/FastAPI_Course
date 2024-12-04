from fastapi import FastAPI, APIRouter
from starlette.responses import HTMLResponse

app = FastAPI(title="Recipe API", openapi_url="/openapi.json")

api_router = APIRouter()


# @api_router.get("/", status_code=200)
# def root() -> dict:
#     """
#     Root GET
#     """
#     return {"msg": "Hello, World!"}

@app.get("/", response_class=HTMLResponse)
async def root():
    # display index.html
    print("Starting")
    with open("index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)

app.include_router(api_router)


if __name__ == "__main__":
    # Use this for debugging purposes only
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
