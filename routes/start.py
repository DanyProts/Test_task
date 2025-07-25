from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from text_batton import start_keyboard, text_get


start_router = Router()


@start_router.message(CommandStart())
async def start(message: Message):
    await message.answer(text_get.t("start.message"), reply_markup=start_keyboard)
