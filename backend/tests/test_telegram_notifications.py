import sys
import os

# Добавляем путь к корню проекта для корректного импорта модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import pytest
from backend.app.services.telegram_templates import booking_message_template

def test_booking_message_template():
    service = "Фотосессия"
    date = "2025-05-12"
    times = ["10:00", "12:00"]
    name = "Иван Иванов"
    phone = "+79991234567"
    total_price = 5000

    expected_message = (
        "🎨 Новое бронирование:\n"
        "Услуга: Фотосессия\n"
        "Дата: 2025-05-12\n"
        "Время: 10:00, 12:00\n"
        "Клиент: Иван Иванов\n"
        "Телефон: +79991234567\n"
        "Сумма: 5000 руб."
    )

    result = booking_message_template(service, date, times, name, phone, total_price)
    assert result == expected_message, "Сообщение Telegram сформировано некорректно"
