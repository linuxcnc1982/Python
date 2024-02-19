from aiogram.types import WebAppInfo
from aiogram import types

web_app = WebAppInfo(url='31.129.49.24')

keyboard = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text='Site', web_app=web_app)]
    ],
    resize_keyboard=True
)
