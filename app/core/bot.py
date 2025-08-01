from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from core import settings


bot = Bot(
    token=str(settings.bot_token.token),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()