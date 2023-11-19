# новые импорты!
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_keyboard_fab(tg_owner_id, sending_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="удалить рассылку",
        callback_data=IdCallbackFactory(action="delete_sending", owner_id=tg_owner_id, sending_id=sending_id)
    )
    return builder.as_markup()


class IdCallbackFactory(CallbackData, prefix="delete_sending"):
    action: str
    owner_id: str
    sending_id: int
