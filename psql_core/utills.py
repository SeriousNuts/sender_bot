import asyncio
from datetime import datetime, timedelta

from sqlalchemy import func, select, text
from sqlalchemy.orm import sessionmaker

from db_models import Account, engine, Schedule, Setting

Session = sessionmaker(bind=engine)
session = Session()


async def insert_account(tg_id, api_code, api_hash, name):
    status = "on"
    account = Account(name, tg_id, api_code, api_hash, status)
    session.add(account)
    session.commit()


async def insert_schedule(period, message_text, owner_tg_id):
    schedule = Schedule()
    schedule.period = int(period)
    schedule.text = message_text
    schedule.next_sending = datetime.now()
    schedule.status = "not sended"
    schedule.owner_tg_id = owner_tg_id
    session.add(schedule)
    session.commit()


async def get_user_schedules(owner_tg_id):
    print("start getting sched")
    schedules = session.query(Schedule).filter(
        Schedule.owner_tg_id == owner_tg_id
    ).all()
    print("stop getting sched")
    return schedules


async def delete_schedule(owner_tg_id, sending_id):
    schedules = session.query(Schedule).filter(Schedule.id == sending_id, Schedule.owner_tg_id == owner_tg_id).first()
    session.delete(schedules)
    session.commit()


async def insert_message(message):
    session.add(message)
    session.commit()


async def get_settings(type_s):
    setting = session.query(Setting).filter(Setting.type == type_s).first()
    account = session.query(Account).filter(Account.name == setting.account).first()
    return setting, account


async def change_account_db(type_s):
    accounts = session.query(Account).filter(Account.status == 'on').all()
    setting = session.query(Setting).filter(Setting.type == type_s).first()
    for i, a in enumerate(accounts):
        if a.name == setting.account:
            setting.account = accounts[(i + 1) % len(accounts)].name
            a.last_use_up(30)
            session.add(a)
            break
    session.add(setting)
    session.commit()
