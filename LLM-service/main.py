import logging
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telethon import TelegramClient
from core import settings
from crud import check_channel_access
from crud import ChannelAccessStatus
import uvicorn

app = FastAPI()
logging.basicConfig(level=logging.INFO)


client = TelegramClient(
    "my_session",
    int(settings.telethon_set.api_id),
    str(settings.telethon_set.api_hash)
)

class ChannelRequest(BaseModel):
    channel_identifier: str

@app.on_event("startup")
async def startup_event():
    await client.start()
    logging.info("Telethon клиент успешно запущен")

@app.on_event("shutdown")
async def shutdown_event():
    await client.disconnect()
    logging.info("Telethon клиент отключён")

@app.post("/channel_check")
async def check_channel_endpoint(data: ChannelRequest):
    result = await check_channel_access(client, data.channel_identifier)

    if isinstance(result["access_status"], ChannelAccessStatus):
        result["access_status"] = result["access_status"].value

    return result


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8001, reload=True)
