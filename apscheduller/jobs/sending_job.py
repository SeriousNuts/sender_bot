from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from aio_bot.handlers import bot
from aio_bot.pyro_modules.pyro_scripts import *
from db_models import engine, Schedule
from aio_bot.pyro_modules.pyro_scripts import get_channels

Session = sessionmaker(bind=engine)
session = Session()


async def get_schedules():
    schedules = session.query(Schedule).filter(
        Schedule.status != "active", func.extract('minute', func.now() - Schedule.next_sending) > 0
    ).all()
    # update the status column for each user
    for s in schedules:
        s.status = 'active'
    # commit the changes
    session.commit()
    channels = get_channels()
    for s in schedules:
        sended_messages = []
        for ch in channels:
            # print(s.text)
            sm = await send_message_to_tg(text_message=s.text, ch=ch)  # получаем статус отпр сообщения
            sended_messages.append(sm)
        s.status = 'work'
        s.last_sening = datetime.now()
        s.next_sending = datetime.now() + timedelta(minutes=s.period)
        number_mes = len(sended_messages)
        suc_mes = count_messages(sended_messages, 0)
        ban_mes = count_messages(sended_messages, 2)
        flood_mes = count_messages(sended_messages, 3) + count_messages(sended_messages, 1)
        await send_stats_to_user(number_mes=number_mes, suc_mes=suc_mes, ban_mes=ban_mes, flood_mes=flood_mes,
                                 tg_id=s.owner_tg_id)

    session.commit()


def count_messages(sent_messages, code):
    count = {}
    for s in sent_messages:
        count[s.status] = count.get(s.status, 0) + 1

    return count.get(code, 0)


def channels_error(sennded_messages, status):
    errors_messages = []
    for s in sennded_messages:
        if s.status == status:
            errors_messages.append(s.ch)
    return errors_messages


async def send_stats_to_user(number_mes, suc_mes, ban_mes, flood_mes, tg_id, ban_ch):
    if tg_id is None:
        tg_id = "6655978580"
    await bot.send_message(tg_id, f"Совершена рассылка \n "
                                  f"Успешно отправлено в {suc_mes} чатов из {number_mes} \n"
                                  f"В {ban_mes} чатах получен бан \n"
                                  f"Список чатов в которых получен бан: \n"
                                  f"{ban_ch} \n"
                                  f"В {flood_mes} чатах сообщение не отправлено из-за ограничений флуд фильтра канала")

    await bot.session.close()