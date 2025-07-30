import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from core import settings
from db import db_helper
from routes import start_router, manage_channel
from fastapi import FastAPI
import uvicorn
from threading import Thread
from routes import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=str(settings.bot_token.token),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(manage_channel)


app = FastAPI()
app.include_router(api_router, prefix="")

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

async def main():
    
    thread = Thread(target=run_fastapi, daemon=True)
    thread.start()
    try:
        await dp.start_polling(
            bot,
            allowed_updates=Update.model_fields.keys(),
            skip_updates=True,
        )
    finally:
        await db_helper.dispose()

if __name__ == '__main__':
    asyncio.run(main())
