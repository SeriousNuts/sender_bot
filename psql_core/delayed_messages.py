import logging
from datetime import timedelta, datetime

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from db_models import engine, DelayedMessage, Account
from utills.format_erros import format_error_traceback

Session = sessionmaker(bind=engine)
session = Session()


async def add_delayed_message_to_wait(text, schedule_uuid, delay_time, chat_id, owner_tg_id, account, status,
                                      schedule_id):
    delayed_message = DelayedMessage()
    send_time = datetime.now() + timedelta(seconds=delay_time)
    delayed_message.delayedMessage(text=text, schedule_uuid=schedule_uuid, send_time=send_time,
                                   chat_id=chat_id, owner_tg_id=owner_tg_id, account_id=account.get_id(),
                                   status=status, delay_time=delay_time, schedule_id=schedule_id)

    session.add(delayed_message)
    result = True
    try:
        session.commit()
    except Exception as e:
        result = False
        logging.error(f"add_delayedMessage_to_wait error {format_error_traceback(error=e)}")
        session.rollback()
    return result


async def get_account_by_account_id(account_id):
    return session.query(Account).filter(Account.id == account_id).first()


async def get_delayd_messages():
    wait_status = ['ready']
    delayd_messages = session.query(DelayedMessage).filter(
        DelayedMessage.status.in_(wait_status),
        func.extract('minute', func.now() - DelayedMessage.send_time) > 0
    ).order_by(DelayedMessage.account_id).all()
    for dm in delayd_messages:
        dm.set_status('active')
    try:
        session.commit()
    except Exception as e:
        logging.error(f"get delayd message error is {format_error_traceback(error=e)}")
        session.rollback()

    return delayd_messages


async def update_delayed_message_status(message):
    message = session.query(DelayedMessage).filter(DelayedMessage.id == message.id).first()
    message.status = "sended"
    result = True
    try:
        session.commit()
    except Exception as e:
        result = False
        logging.error(f"update_delayed_message_status error is {format_error_traceback(error=e)}")
        session.rollback()
    return result
