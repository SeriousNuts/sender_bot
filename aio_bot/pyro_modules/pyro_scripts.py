import asyncio
import csv
from datetime import datetime
import os
import uuid

from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest, Forbidden, Flood, SessionPasswordNeeded
import logging

from db_models import Message, Setting
from psql_core.utills import insert_message, get_settings

#account_name = "ignat"
#app_id = 28644656
#api_hash = "b79872c0dd5060dd9e6f70f237121810"


# отправляем запрос на регистрацию
async def add_account(app_id_tg, api_hash_tg, phone_number_tg):
    name = str(uuid.uuid4())
    app = Client(str(name), api_id=app_id_tg, api_hash=api_hash_tg)
    if app.is_connected:
        await app.disconnect()
    await app.connect()
    try:
        return await app.send_code(phone_number=phone_number_tg), app
    except BadRequest as e:
        print(f"add client error is: {e.NAME} {e.MESSAGE}")
        return e.NAME


# проверяем код подтверждения клиента
async def check_client_code(code, app, phone_number_tg, phone_hash_tg):
    print("code", code)
    print("phone_hash_tg", phone_hash_tg)
    print("phone_number_tg", phone_number_tg)
    result = ""
    try:
        if app.is_connected:
            auth = await app.sign_in(phone_number=phone_number_tg, phone_code=code,
                                     phone_code_hash=phone_hash_tg.phone_code_hash)
            result = auth
    except BadRequest as e:
        result = e.NAME + " : " + e.MESSAGE
    except SessionPasswordNeeded as e:
        result = e.NAME + " : " + e.MESSAGE
    app.disconnect()
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


async def send_message_to_tg(ch, text_message):
    sended_message = Message()
    settings, account = await get_settings("send")
    app = Client(settings.account, api_id=account.app_id, api_hash=account.api_hash)
    sleep_time = 30
    await app.connect()
    try:
        await app.send_message(str(ch).replace("https://t.me/", ""), text_message)
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=0, channel=ch)
        print(ch, " :IS SENDED")
        await asyncio.sleep(sleep_time)
    except FloodWait as e:
        if app.is_connected:
            if e.value < 300:
                logging.error(f"{datetime.now()} : {str(ch)} FLOOD WAIT MESSAGE WILL BE SENNDED IN LESS {e.value} SECONDS")
                sended_message.set_flood_wait_time(e.value)
                await asyncio.sleep(e.value)
                await app.send_message(str(ch).replace("https://t.me/", ""), text_message)
                sended_message.set_message(text=text_message, sending_date=datetime.now(), status=0, channel=ch)
                await asyncio.sleep(sleep_time)
            else:
                logging.error(f"{datetime.now()} : {str(ch)} FLOOD WAIT {e.value} NOT SENDED")
                sended_message.set_message(text=text_message, sending_date=datetime.now(), status=3, channel=ch)
                sended_message.set_flood_wait_time(e.value)
        else:
            sended_message.set_message(text=text_message, sending_date=datetime.now(), status=2, channel=ch)
    except BadRequest as e:
        print(str(ch), " SENDING ERROR IS", e.NAME)
        logging.error(f"{datetime.now()} : {str(ch)}  SENDING ERROR IS {e.NAME}")
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=2, channel=ch)
    except Forbidden as e:
        print(str(ch), " SENDING ERROR IS", e.NAME)
        logging.error(f"{datetime.now()} : {str(ch)}  SENDING ERROR IS {e.NAME}")
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=1, channel=ch)
    except Flood as e:
        print(str(ch), " SENDING ERROR IS", e.NAME)
        logging.error(f"{datetime.now()} : {str(ch)}  SENDING ERROR IS {e.NAME} WAIT TIME IS {e.value}")
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=3, channel=ch)
        sended_message.set_flood_wait_time(e.value)
    except KeyError as e:
        print(str(ch), " SENDING ERROR IS", str(e))
        logging.error(f"{datetime.now()} : {str(ch)}  SENDING ERROR IS {str(e)}")
        sended_message.set_message(text=text_message, sending_date=datetime.now(), status=5, channel=ch)
    await app.disconnect()
    sended_message.account_name = settings.account
    await insert_message(sended_message)
    return sended_message


async def join_chats_to_tg(ch):
    joined_channels = []
    settings = await get_settings("join")
    app = Client(settings.account)
    await app.connect()
    try:
        await app.join_chat(str(ch).replace("https://t.me/", ""))
        joined_channels.append(ch)
        print(ch, " :IS JOINED")
        await asyncio.sleep(120)
    except FloodWait as e:
        if app.is_connected:
            if e.value < 301:
                print("sleep time is: ", e.value)
                await asyncio.sleep(e.value)
        else:
            await app.disconnect()
            return 0
    except BadRequest as e:
        print(str(ch), " JOINING ERROR IS", e.NAME)
        joined_channels.append(str(ch) + " JOINING ERROR IS" + e.NAME + " : " + e.MESSAGE)
    except Forbidden as e:
        print(str(ch), " JOINING ERROR IS", e.NAME)
        joined_channels.append(str(ch) + " JOINING ERROR IS" + e.NAME + " : " + e.MESSAGE)
    except Flood as e:
        print(str(ch), " JOINING ERROR IS", e.NAME)
        joined_channels.append(str(ch) + " JOINING ERROR IS" + e.NAME + " : " + e.MESSAGE)
    await app.disconnect()
    return joined_channels
