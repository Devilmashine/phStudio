import pytest
from app.services.telegram_templates import booking_message_with_buttons

def test_booking_message_template():
    service = "Фотосессия"
    date = "2025-05-12"
    times = ["10:00", "12:00"]
    name = "Иван Иванов"
    phone = "+79991234567"
    total_price = 5000
    people_count = 3

    expected_message = (
        "🎨 Новое бронирование:\n"
        "Услуга: Студийная фотосессия\n"
        "Дата: 2025-05-12\n"
        "Время: 10:00, 12:00\n"
        "Клиент: Иван Иванов\n"
        "Телефон: +79991234567\n"
        "Количество человек: 3\n"
        "Сумма: 5000 руб."
    )

    result, _ = booking_message_with_buttons(service, date, times, name, phone, total_price, people_count)
    for part in ["Студийная фотосессия", "2025-05-12", "10:00, 12:00", "Иван Иванов", "+79991234567", "5000 руб.", "Количество человек: 3"]:
        assert part in result, f"В сообщении отсутствует: {part}"
