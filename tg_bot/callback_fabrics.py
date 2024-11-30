from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_keyboard_delete_sending(tg_owner_id, sending_id):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="удалить рассылку",
        callback_data=DeleteSendingCallbackFactory(action="delete_sending", owner_id=tg_owner_id, sending_id=sending_id)
    )
    return builder.as_markup()


def get_menu_inline_keyboard():
    add_account_btn = InlineKeyboardButton(
        text="Мои аккаунты",
        url="https://google.com"
    )
    my_accounts_btn = InlineKeyboardButton(
        text="Добавить аккаунт",
        url="https://google.com"
    )
    inline_menu_kb = InlineKeyboardMarkup(inline_keyboard=[[my_accounts_btn], [add_account_btn]])
    return inline_menu_kb


class DeleteSendingCallbackFactory(CallbackData, prefix="delete_sending"):
    action: str
    owner_id: str
    sending_id: int
