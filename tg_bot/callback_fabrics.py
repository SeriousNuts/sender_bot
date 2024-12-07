from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_keyboard_delete_sending(tg_owner_id, sending_id):
    delete_schedule_btn = InlineKeyboardButton(
        text="удалить рассылку",
        callback_data=DeleteSendingCallbackFactory(action="delete_sending", owner_id=tg_owner_id,
                                                   sending_id=sending_id).pack()
    )
    change_schedule_text_btn = InlineKeyboardButton(
        text="Изменить текст рассылки",
        callback_data=ChangeSendingTextCallbackFactory(action="delete_sending", owner_id=tg_owner_id,
                                                       sending_id=sending_id).pack()
    )
    return InlineKeyboardMarkup(inline_keyboard=[[delete_schedule_btn], [change_schedule_text_btn]])


class DeleteSendingCallbackFactory(CallbackData, prefix="delete_sending"):
    action: str
    owner_id: str
    sending_id: int


class ChangeSendingTextCallbackFactory(CallbackData, prefix="change_sending_text"):
    action: str
    owner_id: int
    sending_id: int


def get_menu_inline_keyboard(tg_owner_id):
    add_account_btn = InlineKeyboardButton(
        text="Добавить аккаунт",
        callback_data="add_account"
    )
    my_accounts_btn = InlineKeyboardButton(
        text="Мои аккаунты",
        callback_data=GetMyAccountsCallbackFactory(action="my_accounts", owner_id=tg_owner_id).pack()
    )
    return InlineKeyboardMarkup(inline_keyboard=[[my_accounts_btn], [add_account_btn]])


class GetMyAccountsCallbackFactory(CallbackData, prefix="my_accounts"):
    action: str
    owner_id: int


def get_manage_account_keyboard(tg_owner_id, account_id, account_name):
    delete_account_btn = InlineKeyboardButton(
        text="Удалить аккаунт",
        callback_data=DeletMyAccountCallbackFactory(action="delete_accounts", tg_owner_id=tg_owner_id,
                                                    account_id=account_id).pack()
    )
    change_account_status_btn = InlineKeyboardButton(
        text="Сменить статус",
        callback_data=ChangeMyAccountStatusCallbackFactory(action="change_account_status", tg_owner_id=tg_owner_id,
                                                           account_id=account_id, account_name=account_name).pack()
    )
    return InlineKeyboardMarkup(inline_keyboard=[[delete_account_btn], [change_account_status_btn]])


class DeletMyAccountCallbackFactory(CallbackData, prefix="delete_account"):
    action: str
    owner_id: int
    account_id: int


class ChangeMyAccountStatusCallbackFactory(CallbackData, prefix="change_account_status"):
    action: str
    owner_id: int
    account_id: int
    account_name: str
