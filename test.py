import asyncio
import csv
import logging
import os

from pyrogram import Client
from pyrogram.errors import FloodWait, BadRequest, Forbidden, Flood

from aio_bot.handlers import bot

# account_name = "anatoly"
# app_id = 27544239
# api_hash = "7349da523b2a09c4e502ca71e26c4625"
account_name = "vasily"
app_id = 25180332
api_hash = "539ab72d422f642484190f3a046170b9"
logging.basicConfig(level=logging.ERROR, filename="join_log.log", filemode="a")


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
    chats = get_channels_py()
    results = []
    for c in chats:
        res = await join_chats_to_tg_pyro(c)
        results.append(res)


async def join_chats_to_tg_pyro(ch):
    joined_channels = []
    app = Client(account_name, api_id=app_id, api_hash=api_hash)
    await app.connect()
    try:
        await app.join_chat(str(ch).replace("https://t.me/", ""))
        joined_channels.append(ch)
        logging.error(f"{str(ch)}  JOINED")
        print(ch, " :IS JOINED")
        await asyncio.sleep(120)
    except FloodWait as e:
        if app.is_connected:
            if e.value < 301:
                print("sleep time is: ", e.value)
                await asyncio.sleep(e.value)
                await app.join_chat(str(ch).replace("https://t.me/", ""))
        else:
            await app.disconnect()
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


loop = asyncio.get_event_loop()
loop.run_until_complete(joing_chat())

# asyncio.run(main())
# asyncio.run(get_bio())
# loop = asyncio.get_event_loop()
# loop.run_until_complete(test_send())
