from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from text_batton.language import text_get  

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=text_get.t("menu.add"))],
        [KeyboardButton(text=text_get.t("menu.remove"))],
        [KeyboardButton(text=text_get.t("menu.list"))]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=text_get.t("menu.manage"))]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)
