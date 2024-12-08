from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from db_models import DelayedMessage, Account  # Импортируйте ваши модели
from psql_core.delayed_messages import add_delayed_message_to_wait, get_account_by_account_id, get_delayd_messages, \
    update_delayed_message_status


@pytest.fixture
def mock_session():
    """Создаёт фиктивную сессию SQLAlchemy."""
    session = MagicMock()
    yield session


@pytest.fixture
def mock_delayed_message():
    """Создаёт фиктивный объект DelayedMessage."""
    return MagicMock(spec=DelayedMessage)


@pytest.fixture
def mock_account():
    """Создаёт фиктивный объект Account."""
    account = MagicMock(spec=Account)
    account.get_id.return_value = 1  # Возвращаем фиктивный ID
    return account


@pytest.mark.asyncio
async def test_add_delayed_message_to_wait(mock_session, mock_delayed_message, mock_account):
    """Тест добавления отложенного сообщения."""
    with patch('psql_core.delayed_messages.session', mock_session):
        await add_delayed_message_to_wait("Test message", '123-test-123', 60, "chat_id", "owner_id", mock_account,
                                          "test_ready", schedule_id=None)

        # Проверяем, что сообщение добавлено в сессию
        assert mock_session.add.call_count == 1

        # Проверяем, что commit был вызван
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_add_delayed_message_to_wait_error(mock_session, mock_delayed_message, mock_account):
    """Тест добавления отложенного сообщения."""
    with patch('psql_core.delayed_messages.session', mock_session):
        mock_session.commit = AsyncMock(side_effect=Exception("something wrong"))
        await add_delayed_message_to_wait(text="Test message", schedule_uuid='123-test-123', delay_time=60,
                                          chat_id="chat_id", owner_tg_id=1234, account=mock_account,
                                          status="test_ready",
                                          schedule_id=None)
        # Проверяем, что сообщение добавлено в сессию
        assert mock_session.add.call_count == 1


@pytest.mark.asyncio
async def test_get_account_by_account_id(mock_session, mock_account):
    """Тест получения аккаунта по ID."""
    account = Account()
    account.id = 1
    mock_session.query.return_value.filter.return_value.first.return_value = account

    with patch('psql_core.delayed_messages.session', mock_session):
        account = await get_account_by_account_id(1)

        # Проверяем, что запрос был выполнен с правильным ID
        assert account.id == 1


@pytest.mark.asyncio
async def test_get_delayd_messages(mock_session, mock_delayed_message):
    """Тест получения отложенных сообщений."""
    mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_delayed_message]

    with patch('psql_core.delayed_messages.session', mock_session):
        messages = await get_delayd_messages()

        # Проверяем, что статус сообщений изменён на 'active'
        assert mock_delayed_message.set_status.call_count == 1

        # Проверяем, что commit был вызван
        mock_session.commit.assert_called_once()

        # Проверяем возвращаемые сообщения
        assert messages == [mock_delayed_message]


@pytest.mark.asyncio
async def test_update_delayed_message_status(mock_session, mock_delayed_message):
    """Тест обновления статуса отложенного сообщения."""
    mock_session.query.return_value.filter.return_value.first.return_value = mock_delayed_message

    with patch('psql_core.delayed_messages.session', mock_session):
        await update_delayed_message_status(mock_delayed_message)

        # Проверяем, что статус сообщения изменён на 'sended'
        assert mock_delayed_message.status == "sended"

        # Проверяем, что commit был вызван
        mock_session.commit.assert_called_once()
