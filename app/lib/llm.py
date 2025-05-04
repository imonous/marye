from httpx import AsyncClient
import json

from app.lib.youtube import VideoEntry

class Validator:
    def __init__(self, api_key: str, client: AsyncClient):
        self.api_key = api_key
        self.client = client
    
    async def validate(self, video: VideoEntry) -> bool:
        prompt =  (
        """
        You are an AI classifier. Given a YouTube video title, description and 
        (optionally) tags determine whether the video is *purely* educational. 
        Respond with only 'True' if the video is educational, otherwise 'False'.
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
                            "text": video.promptify()
                        }
                    ]
                }
            ]
        }
        response = await self.client.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
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