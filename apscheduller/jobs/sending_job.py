from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from aio_bot.handlers import bot
from aio_bot.pyro_modules.pyro_scripts import *
from db_models import engine, Schedule
from psql_core.utills import get_accounts_by_schedule

Session = sessionmaker(bind=engine)
session = Session()


async def get_schedules():
    schedules = session.query(Schedule).filter(
        Schedule.status != "active", Schedule.status != "test",
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
        for acc in accounts:
            app = await get_app_by_session_string(session_string=acc.session_string, app_name=acc.name)
            channels = await get_channels_by_app(app)
            tasks_queue.append(asyncio.create_task(send_message_to_tg(text_message=s.text, app=app, channels=channels,
                                                                      account_name=acc.name,
                                                                      schedule_owner_id=s.owner_tg_id)))
    await asyncio.gather(*tasks_queue)  # ожидаем завершения всех задач на отправку сообщений
    for s in schedules:
        s.last_sening = datetime.now()
        s.next_sending = datetime.now() + timedelta(minutes=s.period)
        s.status = "work"
    session.commit()


def count_messages(sent_messages, code):
    count = {}
    for s in sent_messages:
        count[s.status] = count.get(s.status, 0) + 1
    return count.get(code, 0)


def channels_error(sended_messages, status):
    errors_messages = []
    for s in sended_messages:
        if s.status == status:
            errors_messages.append(s.channel)
    return errors_messages


def send_stats_to_user(number_mes, suc_mes, ban_mes, flood_mes, tg_id, ban_ch, flood_ch):
    message = (f"Совершена рассылка \n " +
               f"Успешно отправлено в {suc_mes} чатов из {number_mes} \n" +
               f"В {ban_mes} чатах получен бан \n" +
               f"В {flood_mes} чатах сообщение не отправлено из-за ограничений флуд фильтра канала")
    if len(message) >= 4090:
        message = message[1:4000]
    try:
        bot.send_message(tg_id, message)
    except Exception as e:
        logging.error(f"send stats to user error: {e} \n error in {e.__traceback__}")
