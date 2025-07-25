from aiogram import Bot, Dispatcher
from routes import start_router, manage_channel
from core.config import settings
import asyncio

bot = Bot(str(settings.bot_token.token))
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(manage_channel)


async def main():


    await dp.start_polling(bot)

if __name__=='__main__':
    asyncio.run(main())