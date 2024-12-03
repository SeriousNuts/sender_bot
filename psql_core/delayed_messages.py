import logging
from datetime import timedelta, datetime

from sqlalchemy.orm import sessionmaker
from db_models import engine, DelayedMessage, Account
from utills.format_erros import format_error_traceback

Session = sessionmaker(bind=engine)
session = Session()


async def add_delayed_message_to_wait(text, schedule_id, delay_time, chat_id, owner_tg_id, account, status):
    delayed_message = DelayedMessage()
    send_time = datetime.now() + timedelta(seconds=delay_time)
    delayed_message.delayedMessage(text=text, schedule_id=schedule_id, send_time=send_time,
                                   chat_id=chat_id, owner_tg_id=owner_tg_id, account_id=account.get_id(), status=status)

    session.add(delayed_message)

    try:
        session.commit()
    except Exception as e:
        logging.error(f"add_delayedMessage_to_wait error {format_error_traceback(error=e)}")
        session.rollback()


async def get_account_by_account_id(account_id):
    return session.query(Account).filter(Account.id == account_id).first()


async def get_delayd_messages():
    wait_status = ['ready']
    delayd_messages = session.query(DelayedMessage).filter(
        DelayedMessage.status.in_(wait_status)
    ).order_by(DelayedMessage.account_id).all()
    for dm in delayd_messages:
        dm.set_status('active')
    try:
        session.commit()
    except Exception as e:
        logging.error(f"get delayd message error is {e.__traceback__}")
        session.rollback()

    return delayd_messages


async def update_delayed_message_status(message):
    message = session.query(DelayedMessage).filter(DelayedMessage.id == message.id).first()
    message.status = "sended"
    try:
        session.commit()
    except Exception as e:
        logging.error(f"update_delayed_message_status error is {e.__traceback__}")
        session.rollback()
