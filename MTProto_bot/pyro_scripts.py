import asyncio
import configparser
import csv
import logging
import os
import uuid
from datetime import datetime

from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest, Forbidden, SessionPasswordNeeded, SlowmodeWait, Flood, \
    TakeoutInitDelay

from db_models import Message
from psql_core.delayed_messages import add_delayed_message_to_wait
from psql_core.utills import insert_message

config = configparser.ConfigParser()
config.read('config.ini')
api_id = int(config['secrets']['api_id'])
api_hash = config['secrets']['api_hash']

'''
скрипты для взаимодействия с API телеграм через pyrogram
'''

# отправляем запрос на регистрацию
async def add_account(phone_number_tg):
    name = str(uuid.uuid4())
    app = Client(str(name), api_id=api_id, api_hash=api_hash, in_memory=True)
    if app.is_connected:
        await app.disconnect()
    await app.connect()
    try:
        return await app.send_code(phone_number=phone_number_tg), app
    except BadRequest as e:
        logging.debug(msg=f"add client error is: {e.NAME} {e.MESSAGE}")
        return e.NAME


# проверяем код подтверждения клиента, если всё ок возвращаем строку сессии
async def check_client_code(code, app, phone_number_tg, phone_hash_tg):
    result = ""
    try:
        if app.is_connected:
            await app.sign_in(phone_number=phone_number_tg, phone_code=code,
                              phone_code_hash=phone_hash_tg.phone_code_hash)
            result = await app.export_session_string()
    except BadRequest as e:
        result = f"error {e.NAME} : {e.MESSAGE}"
        logging.debug(msg=f"check client code error is: {e.NAME} {e.MESSAGE}")
    except SessionPasswordNeeded as e:
        result = f"error {e.NAME} : {e.MESSAGE}"
        logging.debug(msg=f"check client code error is: {e.NAME} {e.MESSAGE}")
    await app.disconnect()
    return result


def get_channels():
    channels = []
    path = os.getcwd()
    channels_path = os.path.join(path, "sender_bot", "aio_bot", "channels.csv")
    with open(channels_path, encoding='UTF-8') as r_file:
        file_reader = csv.DictReader(r_file, delimiter=";")
        for row in file_reader:
            channels.append(row['ссылка на канал'])
    return channels


async def get_app_by_session_string(session_string, app_name):
    return Client(name=app_name, session_string=session_string, in_memory=True)


async def get_channels_by_app(app):
    channels = []
    async with app:
        async for dialog in app.get_dialogs():
            if str(dialog.chat.type) in ["ChatType.GROUP", "ChatType.SUPERGROUP"] and dialog.chat.username is not None:
                channels.append(str(dialog.chat.username))
    return channels


async def send_message_to_tg(text_message, app, channels, account, schedule_owner_id, schedule_uuid,
                             sleep_time=1, max_wait_time=15):
    messages = []
    sending_uuid = uuid.uuid4()
    # формируем очередь сообщений на отправку
    async with app:
        tasks = [send_message_to_channel(app=app, chat_id=ch, text_message=text_message, sending_uuid=sending_uuid,
                                         account=account,
                                         schedule_owner_id=schedule_owner_id, schedule_uuid=schedule_uuid,
                                         max_wait_time=max_wait_time, sleep_time=sleep_time) for ch in channels]
        results = await asyncio.gather(*tasks)
        # сохраняем результат отправки в БД для статистики
        for sended_message in results:
            messages.append(sended_message)
            await insert_message(sended_message)


async def send_message_to_channel(app, chat_id, text_message, sending_uuid,
                                  account, schedule_owner_id, schedule_uuid, max_wait_time, sleep_time):
    sended_message = Message()
    sended_message.sending_uuid = sending_uuid
    sended_message.account_name = account.get_name()
    sended_message.schedule_owner_id = schedule_owner_id
    sended_message.schedule_uuid = schedule_uuid

    try:
        await app.send_message(chat_id=chat_id, text=text_message)
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=0, channel=chat_id)
        await asyncio.sleep(sleep_time)  # Обеспечиваем ожидание между отправками
    except (FloodWait, Flood, SlowmodeWait, TakeoutInitDelay) as e:
        if e.value <= max_wait_time:
            sended_message = await handle_flood_wait(exception=e, app=app, chat_id=chat_id, text_message=text_message,
                                                     sended_message=sended_message, max_wait_time=max_wait_time,
                                                     sleep_time=sleep_time)
        else:
            # если время ожидания слишком велико, отправляем сообщения в длительное ожидание отправки
            await add_delayed_message_to_wait(text=text_message, status='ready', chat_id=chat_id, delay_time=e.value,
                                              owner_tg_id=schedule_owner_id, schedule_id=schedule_uuid, account=account)

    except BadRequest as e:
        logging.debug(f"{chat_id} SENDING ERROR IS {e.NAME} from account:{account.get_name()}")
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=2, channel=chat_id)
    except Forbidden as e:
        logging.debug(f"{chat_id} SENDING ERROR IS {e.NAME} from account:{account.get_name()}")
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=1, channel=chat_id)
    except KeyError as e:
        logging.debug(f"{chat_id} SENDING ERROR IS {str(e)} from account:{account.get_name()}")
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=5, channel=chat_id)
    except Exception as e:
        logging.error(f"{chat_id} Unknown error while sending on channel: from account: {account.get_name()}: {e}")

    return sended_message


async def handle_flood_wait(exception, app, chat_id, text_message, sended_message, max_wait_time, sleep_time):
    wait_time = min(exception.value or sleep_time, max_wait_time)  # Ограничиваем максимальное время ожидания
    logging.debug(f"{chat_id} FLOOD WAIT {wait_time} seconds")
    sended_message.set_flood_wait_time(wait_time)
    await asyncio.sleep(wait_time)
    try:
        await app.send_message(chat_id=chat_id, text=text_message)
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=0, channel=chat_id)
        await asyncio.sleep(sleep_time)  # Обеспечиваем ожидание между отправками
    except (FloodWait, Flood, SlowmodeWait, TakeoutInitDelay) as retry_exception:
        sended_message.set_flood_wait_time(retry_exception.value + wait_time)
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=3, channel=chat_id)
        logging.debug(f"{chat_id} still in flood wait: {retry_exception.value}")
    return sended_message
