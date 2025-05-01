from httpx import AsyncClient
import json
from dotenv import load_dotenv
import os

from app.lib.youtube import VideoContext

load_dotenv()
or_api = os.getenv("OPENROUTER_API")


class Marye:
    def __init__(self, api_key: str, client: AsyncClient):
        self.api_key = api_key
        self.client = client

    
    async def validate_video(self, video_ctx: VideoContext) -> bool:
        # with open("prompt.txt", "r") as f:
        #     prompt = f.read()
        prompt =  (
            """
            You are an AI classifier. Given a YouTube video title, description and 
            (not always) tags determine whether the video is *purely* educational. Respond 
            only 'True' if the video is educational, otherwise 'False'.
            """
        )
        payload = {
            # "model": "google/gemini-2.5-pro-exp-03-25:free",
            "model": "meta-llama/llama-4-maverick:free",
            "messages": [
                {
                    "role": "system",
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
                            "text": video_ctx.promptify()
                        }
                    ]
                }
            ]
        }
        response = await self.client.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {or_api}",
                "Content-Type": "application/json"
            },
            data=json.dumps(payload)
        )
        response.raise_for_status()
        try:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            if answer in ["True", "False"]:
                return True if answer == "True" else False
            raise RuntimeError()
        except:
            raise RuntimeError("Unable to parse the response.", data)