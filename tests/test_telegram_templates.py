import pytest
from backend.app.services.telegram_templates import booking_message_with_buttons

def test_booking_message_with_buttons_valid():
    msg, buttons = booking_message_with_buttons(
        service="Студийная фотосессия",
        date="22.05.2025",
        times=["10:00", "11:00"],
        name="Тест Клиент",
        phone="79999999999",
        total_price=2500,
        people_count=3
    )
    assert "Студийная фотосессия" in msg
    assert "22.05.2025" in msg
    assert "10:00, 11:00" in msg
    assert "Тест Клиент" in msg
    assert "79999999999" in msg
    assert "2500 руб." in msg
    assert "Количество человек: 3" in msg
    assert isinstance(buttons, list)

@pytest.mark.parametrize("field,value,error", [
    ("service", "", "Параметр 'service' обязателен и должен быть строкой"),
    ("date", "", "Параметр 'date' обязателен и должен быть строкой"),
    ("times", [], "Параметр 'times' обязателен и должен быть списком строк"),
    ("name", "", "Имя клиента обязательно и должно быть строкой"),
    ("phone", "", "Телефон клиента обязателен и должен быть строкой"),
    ("total_price", 0, "Цена должна быть больше 0"),
    ("people_count", 0, "Количество человек обязательно и должно быть положительным целым числом"),
])
def test_booking_message_with_buttons_invalid(field, value, error):
    kwargs = dict(
        service="Студийная фотосессия",
        date="22.05.2025",
        times=["10:00", "11:00"],
        name="Тест Клиент",
        phone="79999999999",
        total_price=2500,
        people_count=2
    )
    kwargs[field] = value
    with pytest.raises(ValueError) as exc:
        booking_message_with_buttons(**kwargs)
    assert error in str(exc.value)
