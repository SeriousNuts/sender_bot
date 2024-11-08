from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from aio_bot.handlers import bot
from aio_bot.pyro_modules.pyro_scripts import *
from db_models import engine, Schedule

logging.basicConfig(level=logging.ERROR, filename="py_log.log", filemode="a")
Session = sessionmaker(bind=engine)
session = Session()


# noinspection PyBroadException
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




# noinspection DuplicatedCode
async def send_messages():
    schedules = await get_schedules()  # получаем список заданий
    for s in schedules:
        sended_messages = []
        send_tasks = []
        app = get_app_by_session_string(session_string=session_string)
        channels = get_channels_by_app(app)
        send_task = asyncio.create_task(send_message_to_tg(text_message=s.text, app=app, channels=channels, settings=s.settings))
        send_tasks.append(send_task)
    await asyncio.gather(*send_tasks)  # ожидаем завершения всех задач на отправку сообщений

    for send_task in send_tasks:
        sm = send_task.result()  # получаем результат отправки сообщения
        sended_messages.append(sm)

    s.last_sening = datetime.now()
    s.next_sending = datetime.now() + timedelta(minutes=s.period)
    number_mes = len(sended_messages)
    suc_mes = count_messages(sended_messages, 0)
    ban_mes = count_messages(sended_messages, 2)
    flood_mes = count_messages(sended_messages, 3) + count_messages(sended_messages, 1)
    ban_ch = channels_error(sended_messages, 2)
    flood_ch = channels_error(sended_messages, 3)
    send_stats_to_user(number_mes=number_mes, suc_mes=suc_mes, ban_mes=ban_mes, flood_mes=flood_mes,
                       tg_id=s.owner_tg_id, ban_ch=ban_ch, flood_ch=flood_ch)
    s.status = 'work'
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
               f"Список чатов в которых получен бан: \n" +
               f"{ban_ch} \n" +
               f"В {flood_mes} чатах сообщение не отправлено из-за ограничений флуд фильтра канала" +
               f"список чатов куда сообщение не ушло из-за ограничений телеграма:\n {flood_ch}")
    if len(message) >= 4090:
        message = message[1:4000]
    if tg_id is None:
        tg_id = "6655978580"
    try:
        bot.send_message(tg_id, message)
    except Exception as e:
        logging.error(f"send stats to user error: {e} \n error in {e.__traceback__}")
