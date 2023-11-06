from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, func
from aio_bot.scripts import *
from db_models import engine, Schedule
from sqlalchemy import select, update
from datetime import datetime, timedelta
from aio_bot.scripts.pyro_scripts import *

Session = sessionmaker(bind=engine)
session = Session()


async def get_schedules():
    schedules = session.query(Schedule).filter(
        Schedule.status != "active", func.extract('minute', func.now() - Schedule.next_sending) > 0
    ).all()
    # update the status column for each user
    for s in schedules:
        s.status = 'active'
    # commit the changes
    session.commit()
    sended_messages = []
    for s in schedules:
        print(s.text)
        sm = await send_message_to_tg(text_message=s.text, ch="https://t.me/zapashdgu")
        sended_messages.append(sm)
        s.status = 'work'
        s.last_sening = datetime.now()
        s.next_sending = datetime.now() + timedelta(minutes=s.period)
    session.commit()


# get_schedules()
# loop = asyncio.get_event_loop()
#
#
# async def create_tasks_func():
#     tasks = list()
#     tasks.append(asyncio.create_task(get_schedules()))
#     await asyncio.wait(tasks)
#
#
# loop.run_until_complete(create_tasks_func())
# loop.close()
