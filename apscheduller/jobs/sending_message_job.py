from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from MTProto_bot.pyro_scripts import *
from db_models import engine, Schedule
from psql_core.utills import get_accounts_by_tg_id
from utills.stats_format import send_schedule_stats_to_user

Session = sessionmaker(bind=engine)
session = Session()


async def get_schedules():
    blocker_status = ["active", "test"]
    schedules = session.query(Schedule).filter(
        Schedule.status.notin_(blocker_status),
        func.extract('minute', func.now() - Schedule.next_sending) > 0
    ).all()
    for s in schedules:
        s.status = 'active'
    try:
        session.commit()
    except Exception as e:
        logging.error(f"get schedulles error is {e.__traceback__}")
        session.rollback()
    return schedules


async def send_messages():
    schedules = await get_schedules()  # получаем список заданий
    #tasks_queue = []
    schedule_uuid_list = []
    for s in schedules:
        accounts = await get_accounts_by_tg_id(tg_id=s.owner_tg_id)
        schedule_uuid = str(uuid.uuid4())
        schedule_uuid_list.append(schedule_uuid)
        for acc in accounts:
            app = await get_app_by_session_string(session_string=acc.session_string, app_name=acc.name)
            channels = await get_channels_by_app(app)
            await send_message_to_tg(text_message=s.text, app=app, channels=channels,
                                                                      account=acc,
                                                                      schedule_owner_id=s.owner_tg_id,
                                                                      schedule_uuid=schedule_uuid,
                                                                      schedule_id=s.id)
    #await asyncio.gather(*tasks_queue)  # ожидаем завершения всех задач на отправку сообщений
    for index, s in enumerate(schedules):
        try:
            s.last_sening = datetime.now()
            s.next_sending = datetime.now() + timedelta(minutes=s.period)
            s.status = "work"
            await send_schedule_stats_to_user(schedule_uuid=schedule_uuid_list[index], schedule_owner_id=s.owner_tg_id,
                                              schedule_text=s.text)
        except Exception as e:
            logging.error(f"Error updating schedule {s.id}: {e}")
    try:
        session.commit()
    except Exception as e:
        logging.error(f"Error committing session in send message: {e}")
        session.rollback()
