import configparser

from aiogram import Bot, Dispatcher, Router
from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.markdown import hbold

from tg_bot import buttons
from tg_bot.buttons import *
from tg_bot.callback_fabrics import get_keyboard_delete_sending, DeleteSendingCallbackFactory, get_menu_inline_keyboard
from tg_bot.models.Forms import StartSendingForm, SignUpForm
from MTProto_bot.pyro_scripts import get_channels, send_message_to_tg, add_account, \
    check_client_code
from psql_core.utills import *
from utills.phone_check import *

config_ini = configparser.ConfigParser()
config_ini.read('config.ini')
TOKEN = config_ini['secrets']['bot_token']
PAYMENTS_TOKEN = config_ini['secrets']['payments_token']

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
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} "
                           f"{message.successful_payment.currency} прошел успешно!!!")


@dp.message(F.text.lower() == "создать рассылку")
async def get_text(message: Message, state: FSMContext) -> None:
    await message.reply(f"Начинаем формирование рассылки для отмены введите /cancel",
                        reply_markup=ReplyKeyboardRemove())
    await message.reply(f"Введите сообщение которое будем рассылать", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StartSendingForm.text)


# запрос интервала рассылки
@dp.message(StartSendingForm.text)
async def get_interval(message: Message, state: FSMContext) -> str:
    if message.text == "/cancel":
        await state.clear()
        await message.reply(f"Создание рассылки отменено", reply_markup=buttons.menu_keyboard)
        return ""
    await state.update_data(text=message.text)
    await message.reply(f"Отлично, текст записал", reply_markup=ReplyKeyboardRemove())
    await message.reply(f"Теперь введите интервал в минутах для рассылки", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StartSendingForm.interval)


@dp.message(StartSendingForm.interval)
async def start_sending(message: Message, state: FSMContext) -> str:
    if message.text == "/cancel":
        await state.clear()
        await message.reply(f"Создание рассылки отменено", reply_markup=buttons.menu_keyboard)
        return ""
    await state.update_data(interval=message.text)
    data = await state.get_data()
    interval = data["interval"]
    sending_message_text = data["text"]
    await insert_schedule(period=interval, message_text=sending_message_text, owner_tg_id=message.from_user.id)
    await message.reply(
        f"Будем отправлять ваш текст раз в {interval} минут. После каждой отправки вам придёт статистика",
        reply_markup=ReplyKeyboardRemove())
    await message.reply(f"Начинаю отправку", reply_markup=buttons.menu_keyboard)
    await state.clear()


# действие на /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await insert_user(message.from_user.id)
    await message.reply(f"Привет, {hbold(message.from_user.full_name)}!", reply_markup=buttons.menu_keyboard)


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
        sended_message = await send_message_to_tg(ch, "test")
        msg = await msg.edit_text(f"{msg.text}\n {sended_message}", disable_web_page_preview=True)
    await message.answer(f"Все сообщения отправлены")


@dp.message(Command("cancel"))
async def test_handler(state: FSMContext) -> None:
    await state.clear()


@dp.message(F.text.lower() == "мои рассылки")
async def menu(message: Message) -> None:
    schedules = await get_user_schedules(str(message.from_user.id))
    if len(schedules) == 0:
        await message.reply(f"У вас нет ни одной рассылки. Можете создать их выбрав в /menu 'Создать рассылку'")
    else:
        for s in schedules:
            await bot.send_message(message.from_user.id, f"Текст рассылки:\n {s.text}\n Период: {s.period}",
                                   reply_markup=get_keyboard_delete_sending(sending_id=s.id,
                                                                            tg_owner_id=str(message.from_user.id))
                                   )


@dp.callback_query(DeleteSendingCallbackFactory.filter(F.action == "delete_sending"))
async def delete_schedule_callback(query: CallbackQuery, callback_data: DeleteSendingCallbackFactory):
    await delete_schedule(owner_tg_id=callback_data.owner_id, sending_id=callback_data.sending_id)
    await bot.send_message(callback_data.owner_id, f"Сообщение удалено")


@dp.message(F.text.lower() == "menu")
async def get_my_account(message: Message) -> None:
    # получение информации об аккаунте
    await bot.send_message(message.from_user.id, "ID аккаунта:\n"
                                                 f"Баланс:\n"
                                                 f"Аккаунтов для рассылки:", reply_markup=get_menu_inline_keyboard())


@dp.callback_query(F.data == "add_account")
async def add_account_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=f"Введите номер телефона с кодом страны без пробелов для отмены "
             f"введите /cancel"
    )
    await state.set_state(SignUpForm.phone_number)


@dp.message(SignUpForm.phone_number)
async def get_phone(message: Message, state: FSMContext) -> str:
    if message.text == "/cancel":
        await state.clear()
        await message.reply(f"Добавление аккаунта отменено", reply_markup=buttons.menu_keyboard)
        return ""
    if not is_valid_phone_number(phone_number=message.text):
        await state.clear()
        await message.reply(f"Введён некорректный номер", reply_markup=buttons.menu_keyboard)
        return ""
    phone_code_hash, app = await add_account(phone_number_tg=message.text)
    await state.update_data(phone_code_hash=phone_code_hash, app=app, phone_number=message.text)
    await bot.send_message(message.chat.id, "Введите код")
    await state.set_state(SignUpForm.user_input_code)


@dp.message(SignUpForm.user_input_code)
async def get_code(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    app = data["app"]
    phone_code_hash = data["phone_code_hash"]
    phone_number = data["phone_number"]
    result = await check_client_code(code=message.text, app=app, phone_number_tg=phone_number,
                                     phone_hash_tg=phone_code_hash)
    if not result.startswith("error"):
        await insert_account(tg_id=message.from_user.id, name=hide_phone_number(phone_number), session_string=result)
        await bot.send_message(message.chat.id, "Аккаунт успешно добавлен")
    else:
        await bot.send_message(message.chat.id, "Ошибка при добавление аккаунта")
    await state.clear()
