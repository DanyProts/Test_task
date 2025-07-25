from typing import Coroutine, Any
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    CallbackQuery,
    InlineKeyboardMarkup
)
from db import get_db, change_active_status
from aiogram.fsm.context import FSMContext
from fsm import ChannelStates
from storage.channel_store import add_channel, remove_channel, list_channels, has_channels
from text_batton import text_get, menu_keyboard


manage_channel = Router()


@manage_channel.message(F.text == text_get.t("menu.manage"))
async def manage_channels(msg: Message) -> Coroutine[Any, Any, None]:
    await msg.answer(text_get.t("menu.prompt"), reply_markup=menu_keyboard)


@manage_channel.message(lambda message: message.text == text_get.t("menu.add"))
async def ask_channel_add(message: Message, state: FSMContext) -> Coroutine[Any, Any, None]:
    async for session in get_db():
        await change_active_status(
            user_id=message.from_user.id,
            session=session
        )

    await message.answer(
        text_get.t("menu.add_prompt"),
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ChannelStates.adding)

@manage_channel.message(ChannelStates.adding)
async def save_channel(msg: Message, state: FSMContext) -> Coroutine[Any, Any, None]:
    add_channel(msg.text)
    await msg.answer(
        text_get.t("menu.added", name=msg.text.strip()),
        reply_markup=menu_keyboard
    )
    await state.clear()


@manage_channel.message(F.text == text_get.t("menu.remove"))
async def ask_channel_remove(msg: Message, state: FSMContext) -> Coroutine[Any, Any, None]:
    channels = list_channels()
    if not channels:
        await msg.answer(text_get.t("menu.empty"))
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=ch, callback_data=f"remove:{ch}")]
            for ch in channels
        ]
    )
    await msg.answer(text_get.t("menu.remove_prompt"), reply_markup=keyboard)


@manage_channel.callback_query(F.data.startswith("remove:"))
async def handle_channel_remove(cbq: CallbackQuery) -> Coroutine[Any, Any, None]:
    channel = cbq.data.split("remove:")[1]
    if remove_channel(channel):
        await cbq.message.edit_text(text_get.t("menu.removed", name=channel))
    else:
        await cbq.message.edit_text(text_get.t("menu.not_found"))


@manage_channel.message(F.text == text_get.t("menu.list"))
async def list_channels_handler(msg: Message) -> Coroutine[Any, Any, None]:
    if not has_channels():
        await msg.answer(text_get.t("menu.empty"))
    else:
        channels_text = "\n".join(f"@{c}" for c in list_channels())
        await msg.answer(text_get.t("menu.list_header", channels=channels_text))
