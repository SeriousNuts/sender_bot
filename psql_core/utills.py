from datetime import datetime

from sqlalchemy.orm import sessionmaker

from db_models import Account, engine, Schedule

Session = sessionmaker(bind=engine)
session = Session()


async def insert_account(tg_id, api_code, api_hash, name):
    status = "0"
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