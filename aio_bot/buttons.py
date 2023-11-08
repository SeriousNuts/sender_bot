from aiogram import types

create_s = [
    [
        types.KeyboardButton(text="создать рассылку"),
    ],
]
create_sending_keyboard = types.ReplyKeyboardMarkup(
    keyboard=create_s,
    resize_keyboard=True,
)
cancel_s = [
    [
        types.KeyboardButton(text="отменить"),
    ],
]
cancel_keyboard = types.ReplyKeyboardMarkup(
    keyboard=cancel_s,
    resize_keyboard=True,
)
