from unittest.mock import MagicMock, patch

import pytest

from psql_core.utills import is_user_have_accounts, insert_account


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