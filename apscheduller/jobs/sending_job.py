from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from tg_bot.handlers import bot
from MTProto_bot.pyro_scripts import *
from db_models import engine, Schedule
from psql_core.get_stats_from_db import get_stats_by_schedule_uuid
from psql_core.utills import get_accounts_by_tg_id

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
    tasks_queue = []
    schedule_uuid_list = []
    for s in schedules:
        accounts = await get_accounts_by_tg_id(tg_id=s.owner_tg_id)
        schedule_uuid = str(uuid.uuid4())
        schedule_uuid_list.append(schedule_uuid)
        for acc in accounts:
            app = await get_app_by_session_string(session_string=acc.session_string, app_name=acc.name)
            channels = await get_channels_by_app(app)
            tasks_queue.append(asyncio.create_task(send_message_to_tg(text_message=s.text, app=app, channels=channels,
                                                                      account_name=acc.name,
                                                                      schedule_owner_id=s.owner_tg_id,
                                                                      schedule_uuid=schedule_uuid)))
    await asyncio.gather(*tasks_queue)  # ожидаем завершения всех задач на отправку сообщений
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


async def send_schedule_stats_to_user(schedule_uuid, schedule_owner_id, schedule_text):
    stats = await get_stats_by_schedule_uuid(schedule_uuid=schedule_uuid)
    message = (f"<b>Совершена рассылка</b> \n" +
               f"<b>Текст: {schedule_text[1:50]}</b> \n" +
               f"<b>Успешно:</b> {stats.sended_message_count}{stats.get_all_message_count()} \n" +
               f"<b>Временный бан:</b> {stats.forbidden_message_count}\n" +
               f"<b>Не прошло флуд фильтр:</b> {stats.flood_wait_message_count}")
    if len(message) >= 4090:
        message = message[1:4000]
    try:
        await bot.send_message(schedule_owner_id, message)
    except Exception as e:
        logging.error(f"send stats to user error: {e} \n error in {e.__traceback__}")
