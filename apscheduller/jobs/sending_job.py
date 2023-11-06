from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from aio_bot.pyro_modules.pyro_scripts import *
from db_models import engine, Schedule

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

