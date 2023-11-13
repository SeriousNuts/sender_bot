# новые импорты!
from typing import Optional
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_keyboard_fab(tg_owner_id, sending_id):
    builder = InlineKeyboardBuilder()
    print("start building")
    builder.button(
        text="удалить рассылку",
        callback_data=IdCallbackFactory(action="change", owner_id=tg_owner_id, sending_id=sending_id)
    )
    print("stop sending button building")
    builder.button(
        text="Подтвердить",
        callback_data=IdCallbackFactory(action="finish")
    )
    builder.adjust(2)
    print("stop building")
    return builder.as_markup()


class IdCallbackFactory(CallbackData, prefix="delete_sending"):
    action: str
    owner_id: Optional[str] = None
    sending_id: Optional[int] = None
