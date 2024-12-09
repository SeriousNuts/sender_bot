from datetime import datetime
import logging

from sqlalchemy.orm import sessionmaker

from db_models import engine, Schedule, DelayedMessage
from utills.format_erros import format_error_traceback

Session = sessionmaker(bind=engine)
session = Session()


async def get_user_schedules(owner_tg_id):
    schedules = session.query(Schedule).filter(
        Schedule.owner_tg_id == owner_tg_id
    ).all()
    return schedules


async def delete_schedule(owner_tg_id, sending_id):
    # noinspection PyTypeChecker
    schedule = session.query(Schedule).filter(Schedule.id == sending_id, Schedule.owner_tg_id == owner_tg_id).first()
    delayed_messages = session.query(DelayedMessage).filter(DelayedMessage.schedule_id == sending_id).all()

    if schedule is not None:
        if len(delayed_messages) > 0:
            for del_m in delayed_messages:
                session.delete(del_m)
        session.delete(schedule)
        try:
            session.commit()
        except Exception as e:
            logging.error(f"delete schedule error {format_error_traceback(error=e)}")
            session.rollback()


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
