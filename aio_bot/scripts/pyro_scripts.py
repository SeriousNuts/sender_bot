import asyncio
import csv
from datetime import datetime
import os
import uuid

from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest, Forbidden, Flood, SessionPasswordNeeded
from aio_bot.scripts.pyro_models import Message
account_name = "my_account"
app_id = 28549543
api_hash = "5901209df83fcf66e27b4cd07f9b81b2"

mes = '🔥🔥🔥 ВНИМАНИЕ 🔥🔥🔥\n\n#продамрекламу #Продам\n\n🔘 Категория:\n#Познавательное, #История,\n\n📢 Канал: ' \
      'История и Секс. \n\nhttps://t.me/historiseks\n\n📈 Подписчиков : 13,9к.+-\nПросмотры за пост 3к+-\n\n💳 Цена  ' \
      '1/24-600\n                  2/24-650\n                  2/48-700🔥🔥\nВозможен ВП\n\nКанал ' \
      'Секселиум\n\nКатегория: Познавательное, Сексология. \n\nhttps://t.me/seksualim\nПодписчиков 9.1к+-\n\nОхват ' \
      '3к+-\nЦена- 1/24-350\n             2/24-400    \n             2/48-450\nВозможен ВП\nКанал ' \
      'Интересно\nhttps://t.me/interesno2028\nКатегория Познавательное\nПодписчиков -3.4к+\nОхват ' \
      '-600+\nЦена-1/24-250\n           2/24-300, \n           2/48-350\nЕСЛИ СРАЗУ В ТРЁХ 1/24-1000\n\nЕСЛИ В ДВУХ ' \
      '1/24-900 РУБ. \n\nОбращаться @A514848 '


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


def get_connection():
    return Client("my_account", api_id=app_id, api_hash=api_hash)


def get_channels():
    channels = []
    path = os.getcwd()
    channels_path = os.path.join(path, "sender_bot", "aio_bot", "channels.csv")
    with open(channels_path, encoding='UTF-8') as r_file:
        file_reader = csv.DictReader(r_file, delimiter=";")
        for row in file_reader:
            channels.append(row['ссылка на канал'])
    return channels


async def send_message_to_tg(ch, text_message):
    sended_messages = Message()
    app = Client(account_name, api_id=app_id, api_hash=api_hash)
    await app.connect()
    try:
        await app.send_message(str(ch).replace("https://t.me/", ""), text_message)
        sended_messages.set_message(text=text_message, sending_date=datetime.now(), status=0, channel=ch)
        print(ch, " :IS SENDED")
        await asyncio.sleep(3)
    except FloodWait as e:
        if app.is_connected:
            if e.value < 120:
                print("sleep time is: ", e.value)
                await asyncio.sleep(e.value)
            else:
                sended_messages.set_message(text=text_message, sending_date=datetime.now(), status=3, channel=ch)
    except BadRequest as e:
        print(str(ch), " SENDING ERROR IS", e.NAME)
        sended_messages.set_message(text=text_message, sending_date=datetime.now(), status=1, channel=ch)
    except Forbidden as e:
        print(str(ch), " SENDING ERROR IS", e.NAME)
        sended_messages.set_message(text=text_message, sending_date=datetime.now(), status=2, channel=ch)
    except Flood as e:
        print(str(ch), " SENDING ERROR IS", e.NAME)
        sended_messages.set_message(text=text_message, sending_date=datetime.now(), status=3, channel=ch)
    await app.disconnect()
    return sended_messages


async def join_chats_to_tg(ch):
    joined_channels = []
    app = Client(account_name, api_id=app_id, api_hash=api_hash)
    await app.connect()
    try:
        await app.join_chat(str(ch).replace("https://t.me/", ""))
        joined_channels.append(ch)
        print(ch, " :IS JOINED")
        await asyncio.sleep(1)
    except FloodWait as e:
        if app.is_connected:
            if e.value < 60:
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
