from unittest.mock import AsyncMock, MagicMock

import pytest
from pyrogram.errors import Forbidden, BadRequest, FloodWait, SlowmodeWait

from aio_bot.pyro_modules.pyro_scripts import send_message_to_tg, get_channels_by_app  # Замените на имя вашего модуля


@pytest.mark.asyncio
async def test_send_message_success():
    # Подготовка
    app = AsyncMock()
    app.send_message = AsyncMock(return_value=None)
    channels = ['channel1', 'channel2']
    text_message = "Hello, World!"
    account_name = "test_account"
    schedule_owner_id = "12345"

    # Вызов функции
    await send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id)

    # Проверка
    assert app.send_message.call_count == len(channels)
    for ch in channels:
        app.send_message.assert_any_call(chat_id=ch, text=text_message)


@pytest.mark.asyncio
async def test_send_message_flood_wait():
    # Подготовка
    app = AsyncMock()
    app.is_connected = True
    app.send_message = AsyncMock(side_effect=[FloodWait(5), None])
    channels = ['channel1']
    text_message = "Hello, World!"
    account_name = "test_account"
    schedule_owner_id = "12345"

    # Вызов функции
    await send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id)

    # Проверка
    assert app.send_message.call_count == 2  # Первый вызов и повторный после ожидания

@pytest.mark.asyncio
async def test_send_message_slowmode_wait():
    # Подготовка
    app = AsyncMock()
    app.is_connected = True
    app.send_message = AsyncMock(side_effect=[SlowmodeWait(5), None])
    channels = ['channel1']
    text_message = "Hello, World!"
    account_name = "test_account"
    schedule_owner_id = "12345"

    # Вызов функции
    await send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id)

    # Проверка
    assert app.send_message.call_count == 2  # Первый вызов и повторный после ожидания

@pytest.mark.asyncio
async def test_send_message_flood_wait_app_is_diconect():
    # Подготовка
    app = AsyncMock()
    app.is_connected = False
    app.send_message = AsyncMock(side_effect=[FloodWait(1)])
    channels = ['channel1']
    text_message = "Hello, World!"
    account_name = "test_account"
    schedule_owner_id = "12345"

    # Вызов функции
    await send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id)

    # Проверка
    assert app.send_message.call_count == 1  # Первый вызов и повторный после ожидания


@pytest.mark.asyncio
async def test_send_message_bad_request():
    # Подготовка
    app = AsyncMock()
    app.send_message = AsyncMock(side_effect=BadRequest("Invalid request"))
    channels = ['channel1']
    text_message = "Hello, World!"
    account_name = "test_account"
    schedule_owner_id = "12345"

    # Вызов функции
    await send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id)

    # Проверка
    assert app.send_message.call_count == 1  # Должен быть только один вызов


@pytest.mark.asyncio
async def test_send_message_forbidden():
    # Подготовка
    app = AsyncMock()
    app.send_message = AsyncMock(side_effect=Forbidden("Access denied"))
    channels = ['channel1']
    text_message = "Hello, World!"
    account_name = "test_account"
    schedule_owner_id = "12345"

    # Вызов функции
    await send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id)

    # Проверка
    assert app.send_message.call_count == 1  # Должен быть только один вызов


@pytest.mark.asyncio
async def test_send_message_key_error():
    # Подготовка
    app = AsyncMock()
    app.send_message = AsyncMock(side_effect=KeyError("Missing key"))
    channels = ['channel1']
    text_message = "Hello, World!"
    account_name = "test_account"
    schedule_owner_id = "12345"

    # Вызов функции
    await send_message_to_tg(text_message, app, channels, account_name, schedule_owner_id)

    # Проверка
    assert app.send_message.call_count == 1  # Должен быть только один вызов


