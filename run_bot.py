import asyncio
import configparser
import logging
import sys

from aiogram import Bot
from aiogram.enums import ParseMode

#from aio_bot.config import TOKEN, TOKEN_TEST
from aio_bot.handlers import dp
config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['secrets']['bot_token']

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot_m = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot_m, skip_updates=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
