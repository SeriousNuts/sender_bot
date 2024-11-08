from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_keyboard_delete_sending(tg_owner_id, sending_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="удалить рассылку",
        callback_data=DeleteSendingCallbackFactory(action="delete_sending", owner_id=tg_owner_id, sending_id=sending_id)
    )
    return builder.as_markup()


def get_menu_inline_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Добавить аккаунт",
        callback_data="add_account"
    )

    return builder.as_markup()


class DeleteSendingCallbackFactory(CallbackData, prefix="delete_sending"):
    action: str
    owner_id: str
    sending_id: int
