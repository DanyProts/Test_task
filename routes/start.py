from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from db import get_db, get_or_create_user
from text_batton import start_keyboard, text_get

start_router = Router()

@start_router.message(CommandStart())
async def start(message: Message):
    async for session in get_db():
        await get_or_create_user(
            user_id=message.from_user.id,
            first_name=message.from_user.first_name,
            session=session
        )
    await message.answer(text_get.t("start.message"), reply_markup=start_keyboard)
