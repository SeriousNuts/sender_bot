from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

create_s = [
    [
        types.KeyboardButton(text="создать рассылку"),
    ],
]
cancel_s = [
    [
        types.KeyboardButton(text="отменить"),
    ],
]
menu_s = [
    [
        types.KeyboardButton(text="создать рассылку"),
        types.KeyboardButton(text="мои рассылки"),
        types.KeyboardButton(text="menu")
    ],
]





cancel_keyboard = types.ReplyKeyboardMarkup(
    keyboard=cancel_s,
    resize_keyboard=True,
)
menu_keyboard = types.ReplyKeyboardMarkup(
    keyboard=menu_s,
    resize_keyboard=True,
)
create_sending_keyboard = types.ReplyKeyboardMarkup(
    keyboard=create_s,
    resize_keyboard=True,
)
delete_sending_inline = InlineKeyboardBuilder()
delete_sending_inline.add(types.InlineKeyboardButton(
    text="Удалить рассылку",
    callback_data="delete_sending")
)
