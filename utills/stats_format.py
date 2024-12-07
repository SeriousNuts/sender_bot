import logging
from datetime import datetime, timedelta

from psql_core.get_stats_from_db import get_stats_by_schedule_uuid, get_stats_by_interval


async def send_schedule_stats_to_user(schedule_uuid, schedule_owner_id, schedule_text):
    from tg_bot.handlers import bot
    stats = await get_stats_by_schedule_uuid(schedule_uuid=schedule_uuid)
    message = (f"<b>Совершена рассылка</b> \n" +
               f"<b>Текст: {schedule_text[0:50]}</b> \n" +
               f"<b>Успешно:</b> {stats.sended_message_count}/{stats.get_all_message_count()} \n" +
               f"<b>Временный бан:</b> {stats.forbidden_message_count}\n" +
               f"<b>Не прошло флуд фильтр:</b> {stats.flood_wait_message_count}\n"
               f"<b>UUID отправки:</b> {schedule_uuid}")
    if len(message) >= 4090:
        message = message[0:4000]
    try:
        await bot.send_message(schedule_owner_id, message,
                               parse_mode='HTML')
    except Exception as e:
        logging.error(f"send stats to user error: {e} \n error in {e.__traceback__}")


async def get_period_stats_by_tg_owner_id(tg_onwer_id: int, days_before: int):
    stats = await get_stats_by_interval(schedule_owner_id=tg_onwer_id, days_before=days_before)
    message = (f"Статистика за последние {days_before} дней\n" +
               f"<b>Успешно:</b> {stats.sended_message_count}\n" +
               f"<b>Всего сообщений</b> {stats.get_all_message_count()}\n" +
               f"<b>Временный бан:</b> {stats.forbidden_message_count}\n" +
               f"<b>Не прошло флуд фильтр:</b> {stats.flood_wait_message_count}")
    return message
