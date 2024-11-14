import asyncio
import configparser
import csv
import logging
import os
import uuid
from datetime import datetime

from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest, Forbidden, SessionPasswordNeeded

from db_models import Message
from psql_core.utills import insert_message

config = configparser.ConfigParser()
config.read('config.ini')
api_id = int(config['secrets']['api_id'])
api_hash = config['secrets']['api_hash']

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
        print(f"add client error is: {e.NAME} {e.MESSAGE}")
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
    except SessionPasswordNeeded as e:
        result = f"error {e.NAME} : {e.MESSAGE}"
    await app.disconnect()
    return result


def get_channels():
    channels = []
    path = os.getcwd()
    channels_path = os.path.join(path, "sender_bot", "aio_bot", "channels.csv")
    #channels_path = os.path.join(path, "aio_bot", "channels_new.csv")
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

async def send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id):
    messages = []
    sleep_time = 1
    sending_uuid = uuid.uuid4()
    async with app:
        for ch in channels:
            sended_message = Message()
            sended_message.sending_uuid = sending_uuid
            sended_message.account_name = account_name
            sended_message.schedule_owner_id = schedule_owner_id
            try:
                await app.send_message(chat_id=ch, text=text_message)
                sended_message.set_message(text=text_message, sending_date=datetime.now(), status=0, channel=ch)
                await asyncio.sleep(sleep_time)
            except FloodWait as e:
                if app.is_connected:
                    if e.value < 15:
                        sended_message.set_flood_wait_time(e.value)
                        await asyncio.sleep(e.value)
                        await app.send_message(chat_id=ch, text=text_message)
                        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=0, channel=ch)
                        await asyncio.sleep(sleep_time)
                    else:
                        logging.debug(f"{datetime.now()} : {str(ch)} FLOOD WAIT {e.value} NOT SENDED")
                        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=3, channel=ch)
                        sended_message.set_flood_wait_time(e.value)
                else:
                    sended_message.set_message(text=text_message, sending_date=datetime.now(), status=2, channel=ch)
            except BadRequest as e:
                print(str(ch), " SENDING ERROR IS", e.NAME)
                logging.debug(f"{datetime.now()} : {str(ch)}  SENDING ERROR IS {e.NAME}")
                sended_message.set_message(text=text_message, sending_date=datetime.now(), status=2, channel=ch)
            except Forbidden as e:
                print(str(ch), " SENDING ERROR IS", e.NAME)
                logging.debug(f"{datetime.now()} : {str(ch)}  SENDING ERROR IS {e.NAME}")
                sended_message.set_message(text=text_message, sending_date=datetime.now(), status=1, channel=ch)
            except KeyError as e:
                print(str(ch), " SENDING ERROR IS", str(e))
                logging.debug(f"{datetime.now()} : {str(ch)}  SENDING ERROR IS {str(e)}")
                sended_message.set_message(text=text_message, sending_date=datetime.now(), status=5, channel=ch)
            messages.append(sended_message)
            await insert_message(sended_message)

