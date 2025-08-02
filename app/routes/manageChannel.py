from typing import Coroutine, Any
from aiogram import Router, F, Bot
from core import bot
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    CallbackQuery,
    InlineKeyboardMarkup,
    ChatMemberUpdated
)
from aiogram.enums import ChatMemberStatus, ChatType
from db import AddChannelResult
from db import get_db, change_active_status, get_user_channels, remove_user_channel, add_user_channel, get_users_by_channel, add_channel, delete_channel
from aiogram.fsm.context import FSMContext
from fsm import ChannelStates
from notify import send_bulk_message, notify_users_remove, get_user_id
from text_batton import text_get, menu_keyboard
from llm_connection import review_post
import logging

manage_channel = Router()
logger = logging.getLogger(__name__)

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
    async for session in get_db():
        result = await add_user_channel(session, msg.from_user.id, msg.text)

        match result["status"]:
            case "added":
                await msg.answer(
                    text_get.t("menu.added", name=result["channel_name"]),
                    reply_markup=menu_keyboard
                )
            case "exists":
                await msg.answer(
                    text_get.t("menu.added.error.channel_ready", name=result["channel_name"]),
                    reply_markup=menu_keyboard
                )
            case "error":
                await msg.answer(
                    result["message"],
                    reply_markup=menu_keyboard
                )

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

@manage_channel.my_chat_member()
async def handle_added_to_channel(event: ChatMemberUpdated, bot: Bot) -> None:
    chat = event.chat

    if chat.type != ChatType.CHANNEL:
        return

    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status

    is_private = chat.username is None
    can_read = new_status in [ChatMemberStatus.ADMINISTRATOR,  ChatMemberStatus.CREATOR]
    
    if old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED] and can_read:
        async for session in get_db():
            await add_channel(session= session, chat= chat, is_private= is_private, can_read= can_read)

    elif new_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        logger.info("Детект удаления бота из канала!")
        async for session in get_db():
            user_id = await get_user_id(session= session, chat= chat)
            if not user_id:
                logger.warning(f"[Удаление канала] Не найден пользователь для канала {chat.id} ({chat.title})")
                return
            await delete_channel(session= session, chat= chat)
            await notify_users_remove(user_ids= user_id, chat= chat, bot= bot)
            


@manage_channel.channel_post()
async def handle_channel_post(post: Message):
    text = post.text
    id = post.chat.id
    LLM_response = await review_post(post_text=text) 
    async for session in get_db():
        user_ids = await get_users_by_channel(session= session, channel_id= id)
        await send_bulk_message(bot= bot,user_ids= user_ids, text= LLM_response)
        logger.info(f"Выполнена рассылка пользователям успешно!")

