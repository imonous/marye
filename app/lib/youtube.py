from datetime import timedelta
from httpx import AsyncClient
import isodate
from pydantic import BaseModel, Field, model_validator

from typing import Any, Optional

# TODO: store multiple res
class Thumbnail(BaseModel):
    url: str
    width: int
    height: int

    def __repr__(self) -> str:
        return f"Thumbnail(url={self.url})"

# TODO: explore other video properties
class VideoEntry(BaseModel):
    id: str
    title: str
    description: str 
    channel_title: str = Field(..., alias="channelTitle")
    published_at: str = Field(..., alias="publishedAt")
    thumbnail: Thumbnail = Field(..., alias="high")
    tags: Optional[list[str]] = None
    duration: timedelta

    def promptify(self) -> str:
        return (
            f"""
            title: "{self.title}"
            description: "{self.description}"
            tags: "{self.tags or []}"
            """
        )

class SearchResult(BaseModel):
    items: list[VideoEntry]
    next_page_token: str

class YouTube:
    URL = "https://www.googleapis.com/youtube/v3"
    SHORT_DURATION = timedelta(seconds=60)

    def __init__(self, api_key: str, client: AsyncClient):
        self.api_key = api_key
        self.client = client
    
    """
    /videos result is not guaranteed to follow the provided order of ids. Hence 
    the extra steps.

    /search only returns partial information (e.g. no video duration). Hence the
    extra search.

    TODO: result validation
    """
    async def search(self, q: str, show_shorts: bool) -> SearchResult:
        resp = await self.client.get(
            f"{YouTube.URL}/search?key={self.api_key}"
            f"&q={q}&part=snippet&type=video&maxResults=50"
        )
        resp.raise_for_status()

        data = resp.json()
        next_page_token = data.get("nextPageToken")
        items = {item["id"]["videoId"]: None for item in data["items"]}

        ids = ",".join(items.keys())
        resp = await self.client.get(
            f"{YouTube.URL}/videos?key={self.api_key}"
            f"&id={ids}&part=snippet,contentDetails"
        )
        resp.raise_for_status()

        data = resp.json()
        for item in data["items"]:
            vid = item["id"]
            dur = item["contentDetails"]["duration"]
            items[vid] = VideoEntry(
                id = vid,
                **item["snippet"],
                **item["snippet"]["thumbnails"],
                duration = isodate.parse_duration(dur)
            )
        
        items = [item for item in items.values() if item is not None]
        if not show_shorts:
            items = [item for item in items if item.duration > YouTube.SHORT_DURATION]
        
        return SearchResult(next_page_token=next_page_token, items=items)
    
    async def get_video_context(self, vid: str) -> VideoEntry:
        resp = await self.client.get(
            f"{YouTube.URL}/videos?key={self.api_key}"
            f"&id={vid}&part=snippet,contentDetails"
        )
        resp.raise_for_status()

        item = resp.json()["items"][0]
        return VideoEntry(
            id = item["id"],
            **item["snippet"],
            **item["snippet"]["thumbnails"],
            duration = isodate.parse_duration(
                item["contentDetails"]["duration"]
            )
        )

    
    async def close(self):
        await self.client.aclose()
