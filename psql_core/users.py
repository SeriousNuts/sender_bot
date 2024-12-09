import logging

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from db_models import engine, User, Account
from utills.format_erros import format_error_traceback

Session = sessionmaker(bind=engine)
session = Session()


async def insert_user(tg_id):
    user = User()
    user.tg_id = tg_id
    session.add(user)
    try:
        session.commit()
    except Exception as e:
        logging.error(f"insert user error {format_error_traceback(error=e)}")
        session.rollback()


async def is_user_have_accounts(user_tg_id):
    return session.query(func.count(Account.id)).filter(Account.owner_tg_id == user_tg_id).scalar() > 0
