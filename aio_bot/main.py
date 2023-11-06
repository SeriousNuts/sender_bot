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

from aio_bot import config, buttons
from aio_bot.models.Forms import StartSendingForm
from scripts.pyro_scripts import get_channels, send_message_to_tg, join_chats_to_tg, add_account, \
    check_client_code
from psql_core.utills import *

TOKEN = config.TOKEN
PAYMENTS_TOKEN = config.PAYMENTS_TOKEN
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


@dp.message(F.text.lower() == "начать рассылку")
async def get_text(message: Message, state: FSMContext) -> None:
    await message.reply(f"Введите сообщение которое будем рассылать", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StartSendingForm.text)


@dp.message(StartSendingForm.text)
async def get_interval(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await message.reply(f"Отлично, текст записал", reply_markup=ReplyKeyboardRemove())
    await message.reply(f"Теперь введите интервал в минутах для рассылки", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StartSendingForm.interval)


@dp.message(StartSendingForm.interval)
async def start_sending(message: Message, state: FSMContext) -> None:
    await state.update_data(interval=message.text)
    data = await state.get_data()
    interval = data["interval"]
    text = data["text"]
    await insert_schedule(period=interval, message_text=text)
    await message.reply(f"Будем отправлять ваш текст раз в {interval} минут", reply_markup=ReplyKeyboardRemove())
    await message.reply(f"Начинаю отправку", reply_markup=ReplyKeyboardRemove())


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.reply(f"Hello, {hbold(message.from_user.full_name)}!", reply_markup=buttons.start_sending_keyboard)


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


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot_m = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot_m, skip_updates=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
