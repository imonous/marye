from dataclasses import dataclass
import requests
import json
from dotenv import load_dotenv
import os
from pprint import pprint

load_dotenv()
or_api = os.getenv("OPENROUTER_API")
yt_api = os.getenv("YOUTUBE_API")

@dataclass
class VideoContext:
    kind: str
    channel_title: str # id in the future?
    description: str
    tags: list[str]
    title: str
    
def get_video_context(id: str):
    response = requests.get(
        url="https://www.googleapis.com/youtube/v3/videos"
            + f"?id={id}"
            + f"&key={yt_api}"
            + f"&part=snippet"
    )
    response.raise_for_status()
    data = response.json()["items"][0]
    return VideoContext(
        data["kind"],
        data["snippet"]["channelTitle"],
        data["snippet"]["description"],
        data["snippet"]["tags"],
        data["snippet"]["title"],
    )

with open("prompt.txt", "r") as f:
    prompt = f.read()

payload = {
    "model": "google/gemini-2.5-pro-exp-03-25:free",
    "messages": [
        {
            "role": "developer",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": str(get_video_context("r91BkCUYbsI"))
                }
            ]
        }
    ]
}

pprint(payload)

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {or_api}",
        "Content-Type": "application/json"
    },
    data=json.dumps(payload)
)

print(response.json())


# cxt = get_video_context("r91BkCUYbsI")
# pprint(cxt)