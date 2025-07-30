from typing import Coroutine, Any
from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    CallbackQuery,
    InlineKeyboardMarkup
)
from db import AddChannelResult
from db import get_db, change_active_status, add_user_channel, get_user_channels, remove_user_channel
from aiogram.fsm.context import FSMContext
from fsm import ChannelStates
from text_batton import text_get, menu_keyboard
from telethon_api import check_channel_access_http


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
    channel_info = await check_channel_access_http(channel_identifier= msg.text.strip())
    if channel_info["access_status"] == "SUCCESS":
        async for session in get_db():
            result = await add_user_channel(
                user_id= msg.from_user.id, 
                channel_id= channel_info["channel_id"],
                channel_name= channel_info["channel_name"], 
                channel_username= channel_info["channel_username"],
                channel_url= channel_info["channel_url"],
                status= channel_info["channel_status"],
                session= session
                )
            await change_active_status(
                user_id=msg.from_user.id,
                session=session
            )
            match result:
                case AddChannelResult.SUCCESS:
                    await msg.answer(text_get.t("menu.added",name = channel_info["channel_name"]),reply_markup=menu_keyboard)
                    
                case AddChannelResult.RELATION_EXISTS:
                    await msg.answer(text_get.t("menu.added.error.channel_ready",name = channel_info["channel_name"]),reply_markup=menu_keyboard)
                    
                case AddChannelResult.USER_NOT_FOUND:
                    print("Пользователь не найден")
                    
                case _:
                    await msg.answer(text_get.t("menu.added.error",name = channel_info["channel_name"]),reply_markup=menu_keyboard)
            await state.clear()
    else:
        await msg.answer(channel_info["error"], reply_markup=menu_keyboard)
        await state.clear()


@manage_channel.message(F.text == text_get.t("menu.remove"))
async def ask_channel_remove(msg: Message) -> Coroutine[Any, Any, None]:
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
            result = "\n".join(f"{i+1}) {c}" for i,c in enumerate(succes))
            await msg.answer(text_get.t("menu.list_header", channels=result))

