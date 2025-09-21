import replicate
import os
from dotenv import load_dotenv
import yaml
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import uvicorn
from pydantic import BaseModel

app = FastAPI()

MAX_TOKENS = 64000

class Message(BaseModel):
    query: str

dotenv_path = '.env'
load_dotenv(dotenv_path=dotenv_path)
api_token = os.getenv('REPLICATE_API_TOKEN')
client = replicate.Client(api_token=api_token)

# Load prompts from prompt.yml
with open("prompt.yml", "r", encoding="utf-8") as f:
    prompts = yaml.safe_load(f)

system_prompt = prompts["system_prompt"]
user_prompt_template = prompts["user_prompt"]

@app.post("/chat")
async def chat(message: Message):
    discord_message = message.query
    user_prompt = user_prompt_template.format(
        user_input=message.query,
        incoming_discord_message=discord_message
    )

    async def generate():
        response = ""
        
        for event in client.stream(
            "anthropic/claude-3.7-sonnet",
            input={
                "prompt": user_prompt,
                "max_tokens": MAX_TOKENS,
                "system_prompt": system_prompt,
                "extended_thinking": False,
                "max_image_resolution": 0.5,
                "thinking_budget_tokens": 1024
            }
        ):
            chunk = str(event)
            response += chunk
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6700)
