from unittest.mock import AsyncMock

import pytest
from pyrogram.errors import Forbidden, BadRequest, FloodWait, SlowmodeWait

from MTProto_bot.pyro_scripts import send_message_to_tg  # Замените на имя вашего модуля

import pytest
from unittest.mock import AsyncMock, MagicMock
from MTProto_bot.pyro_scripts import send_message_to_tg, Message, FloodWait, BadRequest, Forbidden
from db_models import Account


@pytest.fixture
def mock_app():
    """Создаёт фиктивный объект приложения для тестирования."""
    app = AsyncMock()
    return app


@pytest.fixture
def mock_message():
    """Создаёт фиктивный объект сообщения для тестирования."""
    return MagicMock(spec=Message)


@pytest.fixture
def mock_account():
    """Создаёт фиктивный объект аккаунта для тестирования."""
    account_mock = MagicMock(spec=Account)
    account_mock.get_name = '+792TEST1234'
    return MagicMock(spec=Account)


@pytest.mark.asyncio
async def test_send_message_success(mock_app, mock_message, mock_account):
    """Тест успешной отправки сообщения."""
    mock_app.send_message = AsyncMock(return_value=None)

    channels = ['channel1', 'channel2']
    text_message = "Hello, World!"

    await send_message_to_tg(text_message, mock_app, channels, mock_account, "owner_id", "schedule_uuid")

    # Проверка, что сообщение было отправлено дважды
    assert mock_app.send_message.call_count == 2


@pytest.mark.asyncio
async def test_send_message_flood_wait(mock_app, mock_message, mock_account):
    """Тест обработки исключения FloodWait."""
    mock_app.send_message = AsyncMock(side_effect=[FloodWait(2), FloodWait(2)])

    channels = ['channel1']
    text_message = "Hello, World!"

    await send_message_to_tg(text_message, mock_app, channels,  mock_account, "owner_id", "schedule_uuid")

    # Проверка, что сообщение было отправлено дважды (первый раз и повторная попытка)
    assert mock_app.send_message.call_count == 2


@pytest.mark.asyncio
async def test_send_message_bad_request(mock_app, mock_message, mock_account):
    """Тест обработки исключения BadRequest."""
    mock_app.send_message = AsyncMock(side_effect=BadRequest("Bad request error"))

    channels = ['channel1']
    text_message = "Hello, World!"

    await send_message_to_tg(text_message, mock_app, channels, mock_account, "owner_id", "schedule_uuid")

    # Проверка, что сообщение было отправлено один раз
    assert mock_app.send_message.call_count == 1


@pytest.mark.asyncio
async def test_send_message_forbidden(mock_app, mock_message, mock_account):
    """Тест обработки исключения Forbidden."""
    mock_app.send_message = AsyncMock(side_effect=Forbidden("Forbidden error"))

    channels = ['channel1']
    text_message = "Hello, World!"

    await send_message_to_tg(text_message, mock_app, channels, mock_account, "owner_id", "schedule_uuid")

    # Проверка, что сообщение было отправлено один раз
    assert mock_app.send_message.call_count == 1


@pytest.mark.asyncio
async def test_send_message_key_error(mock_app, mock_message, mock_account):
    """Тест обработки исключения KeyError."""
    mock_app.send_message = AsyncMock(side_effect=KeyError("Key error"))

    channels = ['channel1']
    text_message = "Hello, World!"

    await send_message_to_tg(text_message, mock_app, channels, mock_account, "owner_id", "schedule_uuid")

    # Проверка, что сообщение было отправлено один раз
    assert mock_app.send_message.call_count == 1


@pytest.mark.asyncio
async def test_send_unknown_error(mock_app, mock_account):
    """Тест обработки неизвестной ошибки."""
    mock_app.send_message = AsyncMock(side_effect=Exception("Unknown error"))

    channels = ['channel1']
    text_message = "Hello, World!"

    await send_message_to_tg(text_message, mock_app, channels, mock_account, "owner_id", "schedule_uuid")

    # Проверка на то что сообщение было отправлено один раз
    assert mock_app.send_message.call_count == 1


