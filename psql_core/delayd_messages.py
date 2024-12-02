from datetime import timedelta

from sqlalchemy.orm import sessionmaker
from db_models import engine, DelayedMessage

Session = sessionmaker(bind=engine)
session = Session()


def add_delayedMessage_to_db(text, schedule_id, delay_time, chat_id, owner_tg_id, account_id, status):
    delayed_message = DelayedMessage()
    send_time = delay_time + timedelta(seconds=delay_time)
    delayed_message.delayedMessage(text=text, schedule_id=schedule_id, send_time=send_time,
                                   chat_id=chat_id, owner_tg_id=owner_tg_id, account_id=account_id, status=status)

    session.add(delayed_message)
    session.commit()
