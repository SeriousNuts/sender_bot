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
class DeleteSendingCallbackFactory(CallbackData, prefix="delete_sending"):
    action: str
    owner_id: str
    sending_id: int


def get_menu_inline_keyboard(tg_owner_id):
    add_account_btn = InlineKeyboardButton(
        text="Добавить аккаунт",
        callback_data="add_account"
    )
    my_accounts_btn = InlineKeyboardButton(
        text="Мои аккаунты",
        callback_data=GetMyAccountsCallbackFactory(action="delete_sending", owner_id=tg_owner_id).pack()
    )
    inline_menu_kb = InlineKeyboardMarkup(inline_keyboard=[[my_accounts_btn], [add_account_btn]])
    return inline_menu_kb
class GetMyAccountsCallbackFactory(CallbackData, prefix="my_accounts"):
    action: str
    owner_id: str
