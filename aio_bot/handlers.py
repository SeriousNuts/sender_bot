from aiogram import Bot, Dispatcher, types, Router
from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.markdown import hbold

from aio_bot import buttons, config
from aio_bot.buttons import delete_sending_inline
from aio_bot.callback_fabrics import get_keyboard_fab, IdCallbackFactory
from aio_bot.models.Forms import StartSendingForm
from psql_core.utills import *
from aio_bot.pyro_modules.pyro_scripts import get_channels, send_message_to_tg, join_chats_to_tg

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
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    print("SUCCESSFUL PAYMENT:")
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


@dp.message(StartSendingForm.text)
async def get_interval(message: Message, state: FSMContext) -> str:
    if message.text == "/cancel":
        print("/cancel")
        await state.clear()
        await message.reply(f"Создание рассылки отменено", reply_markup=buttons.menu_keyboard)
        return ""
    await state.update_data(text=message.text)
    await message.reply(f"Отлично, текст записал", reply_markup=ReplyKeyboardRemove())
    await message.reply(f"Теперь введите интервал в минутах для рассылки", reply_markup=ReplyKeyboardRemove())
    await state.set_state(StartSendingForm.interval)


@dp.message(StartSendingForm.interval)
async def start_sending(message: Message, state: FSMContext) -> None:
    if message.text == "/cancel":
        print("/cancel")
        await state.clear()
        await message.reply(f"Создание рассылки отменено", reply_markup=buttons.menu_keyboard)
        return ""
    await state.update_data(interval=message.text)
    data = await state.get_data()
    interval = data["interval"]
    text = data["text"]
    await insert_schedule(period=interval, message_text=text, owner_tg_id=message.from_user.id)
    await message.reply(
        f"Будем отправлять ваш текст раз в {interval} минут. После каждой отправки вам придёт стаитсика",
        reply_markup=ReplyKeyboardRemove())
    await message.reply(f"Начинаю отправку", reply_markup=buttons.menu_keyboard)
    await state.clear()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
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


@dp.message(Command("join_chats"))
async def send_messages(message: Message) -> None:
    channels = get_channels()
    msg = await message.answer(f"Начинаем присоеденеие")
    for ch in channels:
        joined_chat = await join_chats_to_tg(ch)
        msg = await msg.edit_text(f"{msg.text}\n {joined_chat}", disable_web_page_preview=True)
    await message.answer(f"Присоеденение к чатам закончено")


@dp.message(Command("cancel"))
async def test_handler(state: FSMContext) -> None:
    await state.clear()


@dp.message(Command("menu"))
async def menu(message: Message) -> None:
    await bot.send_message(message.chat.id, "Меню", reply_markup=buttons.menu_keyboard)


@dp.message(F.text.lower() == "мои рассылки")
async def menu(message: Message) -> None:
    schedules = await get_user_schedules(str(message.from_user.id))
    if len(schedules) == 0:
        await message.reply(f"У вас нет ни одной рассылки. Можете создать их выбрав в /menu 'Создать рассылку'")
    else:
        for s in schedules:
            await bot.send_message(message.from_user.id, f"Текст рассылки:\n {s.text}\n Период: {s.period}",
                                   reply_markup=get_keyboard_fab(sending_id=s.id, tg_owner_id=str(message.from_user.id))
                                   )


@dp.callback_query(IdCallbackFactory.filter(F.action == "delete_sending"))
async def my_callback_foo(query: CallbackQuery, callback_data: IdCallbackFactory):
    print("начало удаления")
    await delete_schedule(owner_tg_id=callback_data.owner_id, sending_id=callback_data.sending_id)
    print("удалено")
    await bot.send_message(callback_data.owner_id, f"Сообщение удалено")


async def send_stats_to_user(number_mes, suc_mes, ban_mes, flood_mes, tg_id, ban_ch):
    if tg_id is None:
        tg_id = "6655978580"
    await bot.send_message(tg_id, f"Совершена рассылка \n "
                                  f"Успешно отправлено в {suc_mes} чатов из {number_mes} \n"
                                  f"В {ban_mes} чатах получен бан \n"
                                  f"Список чатов в которых получен бан: \n"
                                  f"{ban_ch} \n"
                                  f"В {flood_mes} чатах сообщение не отправлено из-за ограничений флуд фильтра канала")