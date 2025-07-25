import asyncio
from contextlib import asynccontextmanager
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import Update
from core import settings
from db import db_helper
from routes import start_router, manage_channel


@asynccontextmanager
async def lifespan(dispatcher: Dispatcher):
    yield
    print("dispose.engine")
    await db_helper.dispose()

bot = Bot(str(settings.bot_token.token), parse_mode = ParseMode.HTML)
dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(manage_channel)


async def main():
    await dp.start_polling(
        bot,
        allowed_updates=Update.__all__,
        skip_updates=True,
        lifespan=lifespan
    )

if __name__=='__main__':
    asyncio.run(main())