import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties
from Telethon import client
from core import settings
from db import db_helper
from routes import start_router, manage_channel



bot = Bot(
    token=str(settings.bot_token.token),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
dp.include_router(start_router)
dp.include_router(manage_channel)

async def main():
    await client.start()
    try:
        await dp.start_polling(
            bot,
            allowed_updates=Update.model_fields.keys(),
            skip_updates=True,
        )
    finally:
        await client.disconnect()
        await db_helper.dispose()

if __name__ == '__main__':
    asyncio.run(main())
