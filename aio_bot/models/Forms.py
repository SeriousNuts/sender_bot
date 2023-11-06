from aiogram.fsm.state import StatesGroup, State


class SignUpForm(StatesGroup):
    app_id = State()
    api_hash = State()
    phone_number = State()
    phone_code_hash = State()
    user_input_code = State()
    app = State()
    chat_id = State()


class StartSendingForm(StatesGroup):
    text = State()
    interval = State()
