from utills.phone_check import is_valid_phone_number, hide_phone_number  # Замените на имя вашего модуля


def test_is_valid_phone_number():
    """Тестируем функцию is_valid_phone_number."""

    # Валидные номера
    assert is_valid_phone_number("79232390755") is True
    assert is_valid_phone_number("+79232390755") is True

    # Невалидные номера
    assert is_valid_phone_number("1234567890123456") is False  # Слишком длинный номер
    assert is_valid_phone_number("12345678901234565465464554") is False  # Слишком длинный номер
    assert is_valid_phone_number("123456") is False  # Слишком короткий номер
    assert is_valid_phone_number("+") is False  # Только знак "+"
    assert is_valid_phone_number("abc123456") is False  # Неправильный формат
    assert is_valid_phone_number("123-456-7890") is False  # Неправильный формат


def test_hide_phone_number():
    """Тестируем функцию hide_phone_number."""

    # Валидные номера для скрытия
    assert hide_phone_number("+79232390755") == "+79*****0755"
    assert hide_phone_number("79516058722") == "795****8722"

    # Невалидные номера
    assert hide_phone_number("12345") == "Неверный номер телефона."
    assert hide_phone_number("+12") == "Неверный номер телефона."
    assert hide_phone_number("invalid") == "Неверный номер телефона."
    assert hide_phone_number("+") == "Неверный номер телефона."
