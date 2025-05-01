from typing import Any
from httpx import AsyncClient
from pydantic import BaseModel, Field, model_validator

# TODO: store multiple res
class Thumbnail(BaseModel):
    url: str
    width: int
    height: int

# TODO: explore other video properties
class VideoEntry(BaseModel):
    id: str = Field(..., alias="videoId")
    kind: str
    title: str
    description: str 
    channel_title: str = Field(..., alias="channelTitle")
    published_at: str = Field(..., alias="publishedAt")
    thumbnail: Thumbnail = Field(default=None, alias="high")
    tags: list[str]
    duration: str = None

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
    next_page_token: str = Field(..., alias="nextPageToken")

class YouTube:
    URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: str, client: AsyncClient):
        self.api_key = api_key
        self.client = client

    async def search(self, q: str) -> SearchResult:
        req = await self.client.get(
            f"{YouTube.URL}/search?key={self.api_key}"
            f"&q={q}&part=snippet&type=video&maxResults=50"
        )
        req.raise_for_status()

        data = req.json()
        data = {
            **data.get("id", {}),
            **data.get("snippet", {}),
            **data.get("snippet", {}).get("thumbnails", {})
        } # flatten

        return SearchResult(**data)
    
    async def deepsearch(self, q: str):
        res = self.search(q)
        ids = ",".join(it.id for it in res.items)
        req = await self.client.get(
            f"{YouTube.URL}/videos?key={self.api_key}"
            f"&id={ids}&part=contentDetails"
        )
        req.raise_for_status()
        data = req.json()
        pass
    
    async def close(self):
        await self.client.aclose()

    # async def get_video_context(self, id: str) -> VideoContext:
    #     req = await self.client.get(
    #         f"{YouTube.URL}/videos"
    #         f"?id={id}&key={self.api_key}&part=snippet"
    #     )
    #     req.raise_for_status()
    #     return VideoContext(**req.json())
