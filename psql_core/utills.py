from sqlalchemy import select, update, insert
from sqlalchemy.orm import sessionmaker
from db_models import Account, Channel, Message, User, engine, Schedule
import uuid
from datetime import datetime

Session = sessionmaker(bind=engine)
session = Session()


async def insert_account(tg_id, api_code, api_hash, name):
    status = "0"
    account = Account(name, tg_id, api_code, api_hash, status)
    session.add(account)
    session.commit()


async def insert_message(user_tg_id, text):
    message = Message()
    message.text = text
    message.user_tg_id = user_tg_id
    session.add(message)
    session.commit()


async def insert_schedule(period, message_text):
    schedule = Schedule()
    schedule.period = int(period)
    schedule.text = message_text
    schedule.next_sending = datetime.now()
    schedule.status = "not sended"
    session.add(schedule)
    session.commit()
