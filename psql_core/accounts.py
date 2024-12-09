import logging

from sqlalchemy.orm import sessionmaker

from db_models import Account, engine, User
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

async def get_accounts_by_tg_id(tg_id):
    # noinspection PyTypeChecker
    return session.query(Account).filter(Account.owner_tg_id == tg_id, Account.status == "on").all()

async def deactivate_account(account_id):
    account = session.query(Account).filter(Account.id == account_id).first()
    account.status = 'Deactivated'
    try:
        session.commit()
    except Exception as e:
        logging.error(f"deactivate account error {format_error_traceback(error=e)}")
        session.rollback()

async def invert_account_status(account_id, tg_owner_id):
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
