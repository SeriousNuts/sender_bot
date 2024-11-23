from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from db_models import Schedule, Account

from psql_core.utills import is_user_have_accounts, insert_account, insert_schedule, delete_schedule, insert_message, \
    get_accounts_by_schedule, get_user_schedules


@pytest.fixture
def mock_session():
    """Создаем фиктивную сессию базы данных."""
    session = MagicMock()
    yield session


@pytest.mark.asyncio
async def test_user_has_accounts(mock_session):
    """Тестируем случай, когда у пользователя есть аккаунты."""
    user_tg_id = 12345

    # Настраиваем поведение mock-сессии
    mock_session.query.return_value.filter.return_value.scalar.return_value = 1

    with patch('psql_core.utills.session', mock_session):
        result = await is_user_have_accounts(user_tg_id)

    assert result is True


@pytest.mark.asyncio
async def test_user_has_no_accounts(mock_session):
    """Тестируем случай, когда у пользователя нет аккаунтов."""
    user_tg_id = 12345

    # Настраиваем поведение mock-сессии
    mock_session.query.return_value.filter.return_value.scalar.return_value = 0

    with patch('psql_core.utills.session', mock_session):
        result = await is_user_have_accounts(user_tg_id)

    assert result is False


@pytest.mark.asyncio
async def test_insert_account_creates_new_account(mock_session):
    """Тестируем создание нового аккаунта."""
    tg_id = 12345
    name = "Test Account"
    session_string = "session_string_example"

    # Создаем имитацию пользователя с пустым списком аккаунтов
    user = MagicMock()
    user.accounts = []

    # Настраиваем поведение mock-сессии
    mock_session.query.return_value.filter.return_value.first.return_value = user

    with patch('psql_core.utills.session', mock_session):
        await insert_account(tg_id, name, session_string)

    # Проверяем, что новый аккаунт был создан и добавлен к пользователю
    assert len(user.accounts) == 1
    account = user.accounts[0]
    assert account.name == name
    assert account.status == "on"
    assert account.session_string == session_string

    # Проверяем, что метод add был вызван на сессии
    mock_session.add.assert_called_once_with(account)

    # Проверяем, что сессия была зафиксирована
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_insert_account_no_user(mock_session):
    """Тестируем случай, когда пользователь не найден."""
    tg_id = 12345
    name = "Test Account"
    session_string = "session_string_example"

    # Настраиваем поведение mock-сессии так, чтобы пользователь не был найден
    mock_session.query.return_value.filter.return_value.first.return_value = None

    with patch('psql_core.utills.session', mock_session):
        await insert_account(tg_id, name, session_string)

    # Проверяем, что метод add не был вызван на сессии
    mock_session.add.assert_not_called()

    # Проверяем, что commit не был вызван
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_insert_schedule_creates_new_schedule(mock_session):
    """Тестируем создание нового расписания."""
    period = 10
    message_text = "Test message"
    owner_tg_id = 12345

    with patch('psql_core.utills.session', mock_session):
        await insert_schedule(period, message_text, owner_tg_id)

    # Проверяем, что новый объект расписания был создан с правильными параметрами
    mock_session.add.assert_called_once()
    added_schedule = mock_session.add.call_args[0][0]  # Получаем добавленный объект

    assert isinstance(added_schedule, Schedule)
    assert added_schedule.period == int(period)
    assert added_schedule.text == message_text
    assert added_schedule.owner_tg_id == owner_tg_id
    assert added_schedule.status == "not sended"
    assert added_schedule.next_sending <= datetime.now()  # Проверяем, что next_sending установлен правильно

    # Проверяем, что метод commit был вызван на сессии
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_insert_schedule_invalid_period(mock_session):
    """Тестируем случай с недопустимым периодом."""
    period = "invalid"  # Неверный тип данных для периода
    message_text = "Test message"
    owner_tg_id = 12345

    with patch('psql_core.utills.session', mock_session):
        with pytest.raises(ValueError):  # Предполагаем, что функция должна выбрасывать ValueError
            await insert_schedule(period, message_text, owner_tg_id)

        # Проверяем, что метод commit не был вызван на сессии
        mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_schedule_success(mock_session):
    """Тестируем успешное удаление расписания."""
    owner_tg_id = 12345
    sending_id = 1

    # Создаем имитацию объекта расписания
    schedule = Schedule()
    schedule.id = sending_id
    schedule.owner_tg_id = owner_tg_id

    # Настраиваем поведение mock-сессии, чтобы возвращать наш объект расписания при запросе
    mock_session.query.return_value.filter.return_value.first.return_value = schedule

    with patch('psql_core.utills.session', mock_session):
        await delete_schedule(owner_tg_id, sending_id)

    # Проверяем, что метод delete был вызван на сессии с правильным объектом
    mock_session.delete.assert_called_once_with(schedule)

    # Проверяем, что метод commit был вызван на сессии
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_schedule_not_found(mock_session):
    """Тестируем случай, когда расписание не найдено."""
    owner_tg_id = 12345
    sending_id = 1

    # Настраиваем поведение mock-сессии так, чтобы ничего не возвращалось при запросе
    mock_session.query.return_value.filter.return_value.first.return_value = None

    with patch('psql_core.utills.session', mock_session):
        await delete_schedule(owner_tg_id, sending_id)

    # Проверяем, что метод delete не был вызван на сессии
    mock_session.delete.assert_not_called()

    # Проверяем, что метод commit не был вызван на сессии
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_insert_message_success(mock_session):
    """Тестируем успешное добавление сообщения."""
    message = "Test message"

    with patch('psql_core.utills.session', mock_session):
        await insert_message(message)

    # Проверяем, что метод add был вызван на сессии с правильным сообщением
    mock_session.add.assert_called_once_with(message)

    # Проверяем, что метод commit был вызван на сессии
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_insert_message_failure(mock_session):
    """Тестируем случай, когда добавление сообщения вызывает исключение."""
    message = "Test message"

    # Настраиваем поведение mock-сессии для выброса исключения при добавлении
    mock_session.add.side_effect = Exception("Database error")

    with patch('psql_core.utills.session', mock_session):
        with pytest.raises(Exception):  # Ожидаем выброс исключения
            await insert_message(message)

        # Проверяем, что метод commit не был вызван на сессии в случае ошибки
        mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_accounts_by_schedule_success(mock_session):
    """Тестируем успешное получение аккаунтов по расписанию."""

    # Создаем имитацию объекта расписания
    schedule = MagicMock()
    schedule.owner_tg_id = 12345

    # Создаем список имитированных аккаунтов
    account1 = Account()
    account1.owner_tg_id = 12345
    account2 = Account()
    account2.owner_tg_id = 12345

    # Настраиваем поведение mock-сессии
    mock_session.query.return_value.filter.return_value.all.return_value = [account1, account2]

    with patch('psql_core.utills.session', mock_session):  # Заменяем на psql_core.utils
        accounts = await get_accounts_by_schedule(schedule)

    # Проверяем, что возвращаемые аккаунты соответствуют ожиданиям
    assert len(accounts) == 2
    assert accounts[0].owner_tg_id == 12345
    assert accounts[1].owner_tg_id == 12345

@pytest.mark.asyncio
async def test_get_accounts_by_schedule_no_accounts(mock_session):
    """Тестируем случай, когда нет аккаунтов по расписанию."""

    # Создаем имитацию объекта расписания
    schedule = MagicMock()
    schedule.owner_tg_id = 12345

    # Настраиваем поведение mock-сессии так, чтобы возвращалось пустое значение
    mock_session.query.return_value.filter.return_value.all.return_value = []

    with patch('psql_core.utills.session', mock_session):  # Заменяем на psql_core.utils
        accounts = await get_accounts_by_schedule(schedule)

    # Проверяем, что возвращаемый список пустой
    assert len(accounts) == 0


@pytest.mark.asyncio
async def test_get_user_schedules_success(mock_session):
    """Тестируем успешное получение расписаний по идентификатору владельца."""

    owner_tg_id = 12345

    # Создаем список имитированных расписаний
    schedule1 = Schedule()
    schedule1.owner_tg_id = owner_tg_id
    schedule2 = Schedule()
    schedule2.owner_tg_id = owner_tg_id

    # Настраиваем поведение mock-сессии
    mock_session.query.return_value.filter.return_value.all.return_value = [schedule1, schedule2]

    with patch('psql_core.utills.session', mock_session):  # Заменяем на psql_core.utills
        schedules = await get_user_schedules(owner_tg_id)

    # Проверяем, что возвращаемые расписания соответствуют ожиданиям
    assert len(schedules) == 2
    assert schedules[0].owner_tg_id == owner_tg_id
    assert schedules[1].owner_tg_id == owner_tg_id


@pytest.mark.asyncio
async def test_get_user_schedules_no_schedules(mock_session):
    """Тестируем случай, когда нет расписаний по идентификатору владельца."""

    owner_tg_id = 12345

    # Настраиваем поведение mock-сессии так, чтобы возвращалось пустое значение
    mock_session.query.return_value.filter.return_value.all.return_value = []

    with patch('psql_core.utills.session', mock_session):  # Заменяем на psql_core.utills
        schedules = await get_user_schedules(owner_tg_id)

    # Проверяем, что возвращаемый список пустой
    assert len(schedules) == 0

