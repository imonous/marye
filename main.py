import requests
import json
from dotenv import load_dotenv
import os
from pprint import pprint


def openrouter_test() -> None:
    or_api = os.getenv("OPENROUTER_API")
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {or_api}",
        },
        data=json.dumps({
            "model": "meta-llama/llama-4-maverick:free",
            "messages": [
                {
                    "role": "user",
                    "content": "What is the meaning of life?"
                }
            ]
        })
    )
    
def youtube_test() -> None:
    yt_api = os.getenv("YOUTUBE_API")

    id = "VCbzASF9Ryg"
    part = "snippet"

    rsp = requests.get(
        url="https://www.googleapis.com/youtube/v3/videos"
            + f"?id={id}"
            + f"&key={yt_api}"
            + f"&part={part}"
    )

    pprint(rsp.json())


if __name__ == "__main__":
    load_dotenv()
    youtube_test()
