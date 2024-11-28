from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from aio_bot.handlers import bot
from aio_bot.pyro_modules.pyro_scripts import *
from db_models import engine, Schedule
from psql_core.get_stats_from_db import get_stats_by_schedule_uuid
from psql_core.utills import get_accounts_by_schedule

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
    for s in schedules:
        accounts = await get_accounts_by_schedule(s)
        schedule_uuid = str(uuid.uuid4())
        for acc in accounts:
            app = await get_app_by_session_string(session_string=acc.session_string, app_name=acc.name)
            channels = await get_channels_by_app(app)
            tasks_queue.append(asyncio.create_task(send_message_to_tg(text_message=s.text, app=app, channels=channels,
                                                                      account_name=acc.name,
                                                                      schedule_owner_id=s.owner_tg_id,
                                                                      schedule_uuid=schedule_uuid)))
        await send_schedule_stats_to_user(schedule_uuid=schedule_uuid, schedule_owner_id=s.owner_tg_id)
    await asyncio.gather(*tasks_queue)  # ожидаем завершения всех задач на отправку сообщений
    for s in schedules:
        s.last_sening = datetime.now()
        s.next_sending = datetime.now() + timedelta(minutes=s.period)
        s.status = "work"

    session.commit()


async def send_schedule_stats_to_user(schedule_uuid, schedule_owner_id):
    stats = await get_stats_by_schedule_uuid(schedule_uuid=schedule_uuid)
    message = (f"Совершена рассылка \n " +
               f"Успешно отправлено в {stats.sended_message_count} чатов из {stats.get_all_message_count()} \n" +
               f"В {stats.forbidden_message_count} чатах получен бан \n" +
               f"В {stats.flood_wait_message_count} чатах сообщение не отправлено из-за ограничений флуд фильтра")
    if len(message) >= 4090:
        message = message[1:4000]
    try:
        await bot.send_message(schedule_owner_id, message)
    except Exception as e:
        logging.error(f"send stats to user error: {e} \n error in {e.__traceback__}")
