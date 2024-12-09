import logging

from sqlalchemy.orm import sessionmaker

from db_models import engine
from utills.format_erros import format_error_traceback

Session = sessionmaker(bind=engine)
session = Session()


async def insert_message(message):
    session.add(message)
    try:
        session.commit()
    except Exception as e:
        logging.error(f"insert message error {format_error_traceback(error=e)}")
        session.rollback()
