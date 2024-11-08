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
    ],
]


def get_menu_inline_keyboard():
    inline_menu = [
        [
            types.InlineKeyboardButton(text="Добавить акаунт", callback_data="add_account")
        ],
    ]
    menu_inline_keyboard = types.InlineKeyboardMarkup(inline_keyboard=inline_menu)
    return menu_inline_keyboard


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
