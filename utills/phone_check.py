import re


def is_valid_phone_number(phone_number):
    # Регулярное выражение для проверки номера телефона
    pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    # Проверка соответствия строки шаблону
    return bool(pattern.match(phone_number) and (16 > len(phone_number) > 10))


def hide_phone_number(phone_number):
    # Проверяем, является ли номер валидным
    if not is_valid_phone_number(phone_number):
        return "Неверный номер телефона."
    # Определяем длину номера
    length = len(phone_number)
    # Скрываем цифры посередине
    if length <= 6:
        return phone_number
    hidden_part = '*' * (length - 7)  # Скрываем все между первой частью и последними 4 цифрами
    return phone_number[:3] + hidden_part + phone_number[-4:]
