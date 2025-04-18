import os
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from pydantic import BaseModel, Field, field_validator, model_validator

# TODO: channel support, live

class Thumbnail(BaseModel):
    url: str
    width: int
    height: int

# filter on kind: youtube#video
# TODO: channel, published Date
class VideoEntry(BaseModel):
    video_id: str = Field(..., alias="videoId")
    title: str
    description: str 
    channel_title: str = Field(..., alias="channelTitle")
    published_at: str = Field(..., alias="publishedAt")
    thumbnail: Thumbnail = Field(default=None, alias="default")

    # TODO: dangerous overrides
    @model_validator(mode="before")
    def flatten(cls, value: Any) -> Any:
        print("---")
        return {
            **value.get("id", {}),
            **value.get("snippet", {}),
            **value.get("snippet", {}).get("thumbnails", {})
        }


class SearchResult(BaseModel):
    items: list[VideoEntry]
    next_page_token: str = Field(..., alias="nextPageToken")

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

load_dotenv()
yt_url = "https://www.googleapis.com/youtube/v3"
yt_api = os.getenv("YOUTUBE_API")

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/search")
async def search(
    q: str, 
    response_model=list[SearchResult]
):
    # async with httpx.AsyncClient() as client:
    #     url = f"{yt_url}/search?key={yt_api}&q={q}&part=snippet"
    #     req = await client.get(url)
    # req.raise_for_status()
    # res = SearchResult(**req.json())

    return {}