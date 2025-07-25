from typing import Coroutine, Any

from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from storage.channel_store import add_channel, remove_channel, list_channels, has_channels

manage_channel = Router()

class ChannelStates(StatesGroup):
    adding: State = State()
    removing: State = State()

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Добавить")],
        [KeyboardButton(text="➖ Удалить")],
        [KeyboardButton(text="📃 Список")]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

@manage_channel.message(F.text == "/channels")
async def manage_channels(msg: Message) -> Coroutine[Any, Any, None]:
    await msg.answer("Управление каналами:", reply_markup=menu_keyboard)

@manage_channel.message(F.text == "➕ Добавить")
async def ask_channel_add(msg: Message, state: FSMContext) -> Coroutine[Any, Any, None]:
    await msg.answer("Пришли username канала (без @):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(ChannelStates.adding)

@manage_channel.message(ChannelStates.adding)
async def save_channel(msg: Message, state: FSMContext) -> Coroutine[Any, Any, None]:
    add_channel(msg.text)
    await msg.answer(f"Канал @{msg.text.strip()} добавлен ✅", reply_markup=menu_keyboard)
    await state.clear()

@manage_channel.message(F.text == "➖ Удалить")
async def ask_channel_remove(msg: Message, state: FSMContext) -> Coroutine[Any, Any, None]:
    channels = list_channels()
    if not channels:
        await msg.answer("Список каналов пуст.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=ch, callback_data=f"remove:{ch}")]
            for ch in channels
        ]
    )
    await msg.answer("Выбери канал для удаления:", reply_markup=keyboard)

@manage_channel.callback_query(F.data.startswith("remove:"))
async def handle_channel_remove(cbq: CallbackQuery) -> Coroutine[Any, Any, None]:
    channel = cbq.data.split("remove:")[1]
    if remove_channel(channel):
        await cbq.message.edit_text(f"Канал @{channel} удалён ❌")
    else:
        await cbq.message.edit_text("Ошибка: канал не найден.")

@manage_channel.message(F.text == "📃 Список")
async def list_channels_handler(msg: Message) -> Coroutine[Any, Any, None]:
    #if not has_channels():
        await msg.answer("Список пуст.")
    #else:
        channels_text = "\n".join(f"@{c}" for c in list_channels())
        await msg.answer("Слежу за:\n" + channels_text)
