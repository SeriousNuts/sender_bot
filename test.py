import asyncio
import csv
import logging
import os
from datetime import timedelta, datetime

from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest, Forbidden, Flood
from sqlalchemy.orm import sessionmaker

from aio_bot.handlers import bot, send_stats_to_user_test
from aio_bot.pyro_modules.pyro_scripts import send_message_to_tg
from apscheduller.jobs.sending_job import count_messages, channels_error
from db_models import Schedule, engine, Setting, Account, Channel

# account_name = "anatoly"
# app_id = 27544239
# api_hash = "7349da523b2a09c4e502ca71e26c4625"
# account_name = "vasily"
# app_id = 25180332
# api_hash = "539ab72d422f642484190f3a046170b9"
account_name = "ignat"
app_id = 28644656
api_hash = "b79872c0dd5060dd9e6f70f237121810"
logging.basicConfig(level=logging.ERROR, filename="join_log.log", filemode="a")
Session = sessionmaker(bind=engine)
session = Session()


async def main():
    async with Client(account_name, app_id, api_hash) as app:
        await app.send_message("me", "Greetings from **Pyrogram**!")
        all_chats = 0
        count = 0
        async for dialog in app.get_dialogs():
            # chat = await app.get_chat(dialog.chat.id)
            # print(dialog.chat.first_name or dialog.chat.title, app.get_chat(dialog.chat.id))
            try:
                if dialog.chat.username is not None:
                    print(f"https://t.me/{dialog.chat.username}; username {dialog.chat.title} type: {dialog.chat.type}")
                    count = count + 1
                all_chats = all_chats + 1
            except Exception:
                print("err")
        print(f"{count}/{all_chats}")


async def get_bio():
    async with Client("anatoly", app_id, api_hash) as app:
        # chat = await app.get_chat("zapashdgu")
        async for dialog in app.get_dialogs():
            if dialog.chat.username == "zapashdgu":
                bio = dialog.chat
                print(bio)


async def test_send():
    await bot.send_message("6655978580", "тестовое сообщение")
    await bot.session.close()


async def joing_chat():
    # chats = ["https://t.me/brukchattg", "https://t.me/TGPR_RealType"]
    chats = get_channels_py()
    # print(chats)
    results = []
    for c in chats:
        res = await join_chats_to_tg_pyro(c)
        results.append(res)
        print(f"{chats.index(c)}/{len(chats)}")


async def join_chats_to_tg_pyro_test(ch):
    joined_channels = []
    app = Client(account_name, api_id=app_id, api_hash=api_hash)
    await app.connect()
    await app.join_chat(str(ch).replace("https://t.me/", ""))
    joined_channels.append(ch)
    # .error(f"{str(ch)}  JOINED")
    print(ch, " :IS JOINED")
    await asyncio.sleep(60)
    await app.disconnect()


async def join_chats_to_tg_pyro(ch):
    joined_channels = []
    app = Client(account_name, api_id=app_id, api_hash=api_hash)
    await app.connect()
    try:
        await app.join_chat(str(ch).replace("https://t.me/", ""))
        joined_channels.append(ch)
        # .error(f"{str(ch)}  JOINED")
        print(ch, " :IS JOINED")
        await asyncio.sleep(120)
    except FloodWait as e:
        if app.is_connected:
            if e.value < 9301:
                print("sleep time is: ", e.value)
                await asyncio.sleep(e.value)
                await app.join_chat(str(ch).replace("https://t.me/", ""))
            else:
                print(f"flood wait too long {e.value}")
                logging.error(f"flood wait too long {e.value}")
                await app.disconnect()
                return 0
        else:
            return 0
    except BadRequest as e:
        print(str(ch), " JOINING ERROR IS", e.NAME)
        joined_channels.append(str(ch) + " JOINING ERROR IS" + e.NAME + " : " + e.MESSAGE)
        logging.error(f"{str(ch)}  JOINING ERROR IS {e.NAME}")
    except Forbidden as e:
        print(str(ch), " JOINING ERROR IS", e.NAME)
        joined_channels.append(str(ch) + " JOINING ERROR IS" + e.NAME + " : " + e.MESSAGE)
        logging.error(f"{str(ch)}  JOINING ERROR IS {e.NAME}")
    except Flood as e:
        print(str(ch), " JOINING ERROR IS", e.NAME)
        joined_channels.append(str(ch) + " JOINING ERROR IS" + e.NAME + " : " + e.MESSAGE)
        logging.error(f"{str(ch)}  JOINING ERROR IS {e.NAME}")
    except KeyError as e:
        print(str(ch), " SENDING ERROR IS", str(e))
        logging.error(f"{str(ch)}  JOINING ERROR IS key error")
        joined_channels.append(str(ch) + " JOINING ERROR IS FLOOD")
    await app.disconnect()
    return joined_channels


def get_channels_py():
    channels = []
    path = os.getcwd()
    channels_path = os.path.join(path, "channels_new.csv")
    # channels_path = os.path.join(path, "aio_bot", "channels_new.csv")
    with open(channels_path, encoding='UTF-8') as r_file:
        file_reader = csv.DictReader(r_file, delimiter=";")
        for row in file_reader:
            channels.append(row['ссылка на канал'])
    return channels


async def send():
    await send_stats_to_user_test("860176121")


async def get_schedules():
    schedules = session.query(Schedule).filter(
        Schedule.status == "test"
    ).all()
    session.commit()
    channels = ["https://t.me/zapashdgu", "https://t.me/ghduudduifd"]
    for s in schedules:
        sended_messages = []
        for ch in channels:
            # print(s.text)
            sm = await send_message_to_tg(text_message=s.text, ch=ch)  # получаем статус отпр сообщения
            sended_messages.append(sm)
        s.last_sening = datetime.now()
        s.next_sending = datetime.now() + timedelta(minutes=s.period)
        number_mes = len(sended_messages)
        suc_mes = count_messages(sended_messages, 0)
        ban_mes = count_messages(sended_messages, 2)
        flood_mes = count_messages(sended_messages, 3) + count_messages(sended_messages, 1)
        ban_ch = channels_error(sended_messages, 2)
        await send_stats_to_user(number_mes=number_mes, suc_mes=suc_mes, ban_mes=ban_mes, flood_mes=flood_mes,
                                 tg_id=s.owner_tg_id, ban_ch=ban_ch)

    session.commit()


def insert_set():
    setting = Setting()
    setting.account = "ignat"
    setting.max_wait_time = 9200
    setting.type = "join"
    session.add(setting)
    session.commit()


def insert_acc():
    account = Account()
    account.status = "on"
    account.name = "ignat"
    account.api_hash = "b79872c0dd5060dd9e6f70f237121810"
    account.app_id = 28644656
    account2 = Account()
    account2.status = "on"
    account2.name = "vasily"
    account2.api_hash = "539ab72d422f642484190f3a046170b9"
    account2.app_id = 25180332
    session.add(account)
    session.add(account2)
    session.commit()


def insert_channels():
    channels = get_channels_py()
    for c in channels:
        chan = Channel()
        chan.url = c
        chan.owner_tg_id = 860176121
        session.add(chan)
    session.commit()

insert_channels()

# loop = asyncio.get_event_loop()
# loop.run_until_complete(joing_chat())
# asyncio.run(get_schedules())
# asyncio.run(main())
# asyncio.run(get_bio())
# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_send())
