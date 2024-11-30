from aiogram.fsm.state import StatesGroup, State


class SignUpForm(StatesGroup):
    phone_number = State()
    phone_code_hash = State()
    user_input_code = State()
    app = State()
    user_id = State()


class StartSendingForm(StatesGroup):
    text = State()
    interval = State()


