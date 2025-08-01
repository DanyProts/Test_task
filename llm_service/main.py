import logging
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from yandex_gpt import get_answer

app = FastAPI()
logging.basicConfig(level=logging.INFO)

class ChannelRequest(BaseModel):
    channel_identifier: str


@app.post("/channel_check")
async def check_channel_endpoint(data: ChannelRequest):
    review_post = get_answer(data.channel_identifier)
    return {"text":review_post}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)
