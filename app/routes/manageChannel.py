from typing import Coroutine, Any
from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    CallbackQuery,
    InlineKeyboardMarkup,
    ChatMemberUpdated
)
from aiogram.enums import ChatMemberStatus, ChatType
from db import AddChannelResult, Channel
from db import get_db, change_active_status, get_user_channels, remove_user_channel, add_user_channel
from aiogram.fsm.context import FSMContext
from fsm import ChannelStates
from text_batton import text_get, menu_keyboard
from sqlalchemy import delete


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

    old_status: str = event.old_chat_member.status
    new_status: str = event.new_chat_member.status

    if old_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED] and \
       new_status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR]:

        try:
            bot_member = await bot.get_chat_member(chat.id, bot.id)
            can_read = bot_member.status in ["administrator", "creator"]
        except Exception:
            can_read = False

        is_private = chat.username is None

        async for session in get_db():
            new_channel = Channel(
                channel_id=chat.id,
                channel_name=chat.title,
                channel_username=chat.username,
                channel_url=f"https://t.me/{chat.username}" if chat.username else None,
                is_private=is_private,
                can_read_posts=can_read
            )
            session.add(new_channel)
            await session.commit()

    elif new_status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
        async for session in get_db():
            stmt = delete(Channel).where(Channel.channel_id == chat.id)
            await session.execute(stmt)
            await session.commit()
