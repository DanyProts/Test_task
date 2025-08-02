from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from text_batton.language import text_get  

#"menu.back": "🔙Назад"

manage_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=text_get.t("menu.add"))],
        [KeyboardButton(text=text_get.t("menu.remove"))],
        [KeyboardButton(text=text_get.t("menu.list"))],
        [KeyboardButton(text=text_get.t("menu.back"))]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=text_get.t("menu.manage"))],
        [KeyboardButton(text=text_get.t("menu.settings"))],
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

set_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=text_get.t("menu.change_role"))],
        [KeyboardButton(text=text_get.t("menu.batton_instruct"))],
        [KeyboardButton(text=text_get.t("menu.back"))]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)
