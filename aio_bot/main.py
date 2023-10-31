import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, types, Router
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from pyrogram.types import User

from models.Forms import SignUpForm
from aio_bot.scripts.pyro_scripts import get_channels, send_message_to_tg, join_chats_to_tg, add_client, check_clinet_code

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6651478266:AAFUIxBM52Z9tuhUC4tLFeWN3Snq8HVEERU"
PAYMENTS_TOKEN = "1744374395:TEST:f1ba47f5bea23611a847"
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=50 * 100)  # в копейках (руб)

# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()


@dp.message(Command("buy"))
async def buy(message: Message) -> None:
    if PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Подписка на бота",
                           description="Активация подписки на бота на 1 месяц",
                           provider_token=PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium"
                                     "-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    print("ok")
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    print("SUCCESSFUL PAYMENT:")
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} "
                           f"{message.successful_payment.currency} прошел успешно!!!")


@dp.message(Command("sign_up"))
async def cmd_sign_up(message: Message, state: FSMContext) -> None:
    msg = await message.answer("Введите APP_ID", reply_markup=ReplyKeyboardRemove())
    await state.update_data(chat_id=str(msg.from_user.id))
    await state.set_state(SignUpForm.app_id)


@dp.message(SignUpForm.app_id)
async def app_id_get(message: Message, state: FSMContext) -> None:
    await state.update_data(app_id=int(message.text.lower()))
    await message.answer("Теперь введите API_HASH", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SignUpForm.api_hash)


@dp.message(SignUpForm.api_hash)
async def api_hash_get(message: Message, state: FSMContext) -> None:
    await state.update_data(api_hash=message.text.lower())
    await message.answer("Теперь введите номер телефона", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SignUpForm.phone_number)


@dp.message(SignUpForm.phone_number)
async def api_hash_get(message: Message, state: FSMContext) -> None:
    await state.update_data(phone_number=message.text.lower())
    user_data = await state.get_data()
    app_code, app = await add_client(app_id_tg=user_data["app_id"], api_hash_tg=user_data["api_hash"],
                                     phone_number_tg=message.text.lower(),
                                     chat_id_tg=user_data["chat_id"])
    await state.update_data(app=app, phone_number=message.text.lower(), phone_code_hash=app_code)
    await message.answer("введите код", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SignUpForm.user_input_code)


@dp.message(SignUpForm.user_input_code)
async def api_hash_get(message: Message, state: FSMContext) -> None:
    await state.update_data(user_input_code=message.text.lower())
    user_data = await state.get_data()
    check_code = await check_clinet_code(code=user_data["user_input_code"], app=user_data["app"],
                                         phone_hash_tg=user_data["phone_code_hash"],
                                         phone_number_tg=user_data["phone_number"])
    if not type(check_code) is User:
        await message.answer(f"Регистрация не удалась. Причина :  {str(check_code)}")
    else:
        await message.answer(f"Пользователь {check_code.username} успешно зарегистрирован")
    await state.clear()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message(Command("channel_list"))
async def channels_list(message: Message) -> None:
    channels = get_channels()
    for ch in channels:
        await message.answer(f"Список каналов {ch}")


@dp.message(Command("send_messages"))
async def send_messages(message: Message) -> None:
    channels = get_channels()
    msg = await message.answer(f"Начинаем отправку")
    for ch in channels:
        sended_message = await send_message_to_tg(ch)
        msg = await msg.edit_text(f"{msg.text}\n {sended_message}", disable_web_page_preview=True)
    await message.answer(f"Все сообщения отправлены")


@dp.message(Command("join_chats"))
async def send_messages(message: Message) -> None:
    channels = get_channels()
    msg = await message.answer(f"Начинаем присоеденеие")
    for ch in channels:
        joined_chat = await join_chats_to_tg(ch)
        msg = await msg.edit_text(f"{msg.text}\n {joined_chat}", disable_web_page_preview=True)
    await message.answer(f"Присоеденение к чатам закончено")


# @dp.message()
# async def echo_handler(message: types.Message) -> None:
#     """
#     Handler will forward receive a message back to the sender
#
#     By default, message handler will handle all message types (like a text, photo, sticker etc.)
#     """
#     try:
#         # Send a copy of the received message
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         # But not all the types is supported to be copied so need to handle it
#         await message.answer("Nice try!")


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot_m = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot_m, skip_updates=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
