from typing import Coroutine, Any
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    CallbackQuery,
    InlineKeyboardMarkup
)
from db.models import AddChannelResult
from db import get_db, change_active_status, add_user_channel, get_user_channels, remove_user_channel
from aiogram.fsm.context import FSMContext
from fsm import ChannelStates
from text_batton import text_get, menu_keyboard
from Telethon import client, ChannelAccessStatus, check_channel_access


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
    check_add_possibilities = await check_channel_access(client= client, channel_identifier= msg.text.strip())
    if check_add_possibilities["status"] == ChannelAccessStatus.SUCCESS:
        async for session in get_db():
            result = await add_user_channel(msg.from_user.id, msg.text.strip(), session)
            await change_active_status(
                user_id=msg.from_user.id,
                session=session
            )
            match result:
                case AddChannelResult.SUCCESS:
                    await msg.answer(text_get.t("menu.added",name = msg.text.strip()),reply_markup=menu_keyboard)
                    
                case AddChannelResult.RELATION_EXISTS:
                    await msg.answer(text_get.t("menu.added.error.channel_ready",name = msg.text.strip()),reply_markup=menu_keyboard)
                    
                case AddChannelResult.USER_NOT_FOUND:
                    print("Пользователь не найден")
                    
                case _:
                    await msg.answer(text_get.t("menu.added.error",name = msg.text.strip()),reply_markup=menu_keyboard)
            await state.clear()
    else:
        await msg.answer(check_add_possibilities["error"],name = msg.text.strip(),reply_markup=menu_keyboard)


@manage_channel.message(F.text == text_get.t("menu.remove"))
async def ask_channel_remove(msg: Message, state: FSMContext) -> Coroutine[Any, Any, None]:
    async for session in get_db():
        await change_active_status(
            user_id=msg.from_user.id,
            session=session
        )
        channels = await get_user_channels(user_id=msg.from_user.id, session=session)
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
async def handle_channel_remove(cbq: CallbackQuery):
    channel_name = cbq.data.split("remove:")[1]

    async for session in get_db():
        await change_active_status(
            user_id=cbq.from_user.id,
            session=session
        )
        result = await remove_user_channel(
            user_id=cbq.from_user.id,
            channel_name=channel_name,
            session=session
        )

    match result:
        case AddChannelResult.SUCCESS:
            await cbq.message.edit_text(
                text_get.t("menu.removed", name=channel_name)
            )

        case AddChannelResult.CHANNEL_NOT_FOUND:
            await cbq.message.edit_text(
                text_get.t("menu.not_found")
            )
        case _:
            await cbq.message.edit_text(
                text_get.t("menu.removed.error")
            )


@manage_channel.message(F.text == text_get.t("menu.list"))
async def list_channels_handler(msg: Message) -> Coroutine[Any, Any, None]:
    async for session in get_db():
        succes = await get_user_channels(user_id=msg.from_user.id, session=session)
        if succes == []:
            await msg.answer(text_get.t("menu.empty"))
        else:
            result = "\n".join(f"@{c}" for c in succes)
            await msg.answer(text_get.t("menu.list_header", channels=result))

