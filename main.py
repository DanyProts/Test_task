from aiogram import Bot, Dispatcher
from routes.start import start_router
from core.config import settings
import asyncio

bot = Bot(str(settings.bot_token.token))
dp = Dispatcher()

dp.include_router(start_router)

async def main():
    await dp.start_polling(bot)

if __name__=='__main__':
    asyncio.run(main())