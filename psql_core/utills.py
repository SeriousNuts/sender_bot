import logging
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from db_models import Account, engine, Schedule, User
from utills.format_erros import format_error_traceback

Session = sessionmaker(bind=engine)
session = Session()


async def insert_account(tg_id, name, session_string):
    status = "on"
    account = Account()
    account.account(name=name, status=status, session_string=session_string)
    user = session.query(User).filter(
        User.tg_id == tg_id
    ).first()
    result = False
    if user is not None:
        session.add(account)
        user.accounts.append(account)
        try:
            session.commit()
            result = True
        except Exception as e:
            logging.error(f"insert account error {format_error_traceback(error=e)}")
            session.rollback()

    return result


async def insert_schedule(period, message_text, owner_tg_id):
    schedule = Schedule()
    schedule.period = int(period)
    schedule.text = message_text
    schedule.next_sending = datetime.now()
    schedule.status = "not sended"
    schedule.owner_tg_id = owner_tg_id
    session.add(schedule)
    try:
        session.commit()
    except Exception as e:
        logging.error(f"insert schedule error {format_error_traceback(error=e)}")
        session.rollback()


async def insert_user(tg_id):
    user = User()
    user.tg_id = tg_id
    session.add(user)
    try:
        session.commit()
    except Exception as e:
        logging.error(f"insert user error {format_error_traceback(error=e)}")
        session.rollback()


async def get_user_schedules(owner_tg_id):
    schedules = session.query(Schedule).filter(
        Schedule.owner_tg_id == owner_tg_id
    ).all()
    return schedules


async def delete_schedule(owner_tg_id, sending_id):
    schedules = session.query(Schedule).filter(Schedule.id == sending_id, Schedule.owner_tg_id == owner_tg_id).first()
    if schedules is not None:
        session.delete(schedules)
        try:
            session.commit()
        except Exception as e:
            logging.error(f"delete schedule error {format_error_traceback(error=e)}")
            session.rollback()


async def insert_message(message):
    session.add(message)
    try:
        session.commit()
    except Exception as e:
        logging.error(f"insert message error {format_error_traceback(error=e)}")
        session.rollback()


async def is_user_have_accounts(user_tg_id):
    return session.query(func.count(Account.id)).filter(Account.owner_tg_id == user_tg_id).scalar() > 0


async def get_accounts_by_tg_id(tg_id):
    return session.query(Account).filter(Account.owner_tg_id == tg_id).all()

async def invert_account_status(account_id, tg_owner_id: str):
    account = session.query(Account).filter(Account.id == account_id, Account.owner_tg_id == tg_owner_id).first()
    if account is None:
        return
    account.invert_status()
    session.add(account)
    try:
        session.commit()
    except Exception as e:
        logging.error(f"invert account status error {format_error_traceback(error=e)}")
        session.rollback()
    return account.status
