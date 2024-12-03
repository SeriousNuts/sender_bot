from sqlalchemy.orm import sessionmaker

from MTProto_bot.pyro_scripts import get_app_by_session_string, send_message_to_tg
from db_models import engine
from psql_core.delayed_messages import get_delayd_messages, get_account_by_account_id, update_delayed_message_status

Session = sessionmaker(bind=engine)
session = Session()

'''
чтобы меньше обращаться к телеграму, соортируем эллементы по аккунтам,
 собираем сообщения для каждого аккаунта и отправляем
 стутусы сообщений:
 ready - ждёт отправки, active - подхвачено джобой, sended - отправлено
'''
async def send_delayed_messages():
    messages = await get_delayd_messages()
    if not messages:
        return  # Если нет сообщений, выходим из функции
    current_account = messages[0]
    one_account_messages = []
    for message in messages:
        if message == current_account:
            one_account_messages.append(message)
        else:
            # Отправляем сообщения для предыдущего аккаунта
            await send_one_account_messages(one_account_messages)
            one_account_messages.clear() # Очищаем список для следующего аккаунта
            current_account = message  # Обновляем текущий аккаунт
            one_account_messages.append(message)
    # Отправляем сообщения последнего аккаунта
    if one_account_messages:
        await send_one_account_messages(one_account_messages)


async def send_one_account_messages(one_account_messages):
    account = await get_account_by_account_id(one_account_messages[0].account_id)
    app = await get_app_by_session_string(session_string=account.session_string,
                                          app_name=account.name)
    for oam in one_account_messages:
        await send_message_to_tg(text_message=oam.text, account=account, app=app, channels=[oam.chat_id],
                                 schedule_uuid=oam.schedule_uuid, schedule_owner_id=oam.owner_tg_id)
        await update_delayed_message_status(message=oam)
