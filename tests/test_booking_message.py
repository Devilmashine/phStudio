import unittest
from backend.app.services.telegram_templates import booking_message_with_buttons

class TestBookingMessageWithButtons(unittest.TestCase):
    def test_booking_message_with_valid_data(self):
        service = "Студийная фотосессия"
        date = "2025-05-12"
        times = ["10:00", "12:00"]
        name = "Иван Иванов"
        phone = "+79991234567"
        total_price = 5000

        message, buttons = booking_message_with_buttons(service, date, times, name, phone, total_price)

        expected_message = (
            f"🎨 Новое бронирование:\n"
            f"Услуга: {service}\n"
            f"Дата: {date}\n"
            f"Время: {', '.join(times)}\n"
            f"Клиент: {name}\n"
            f"Телефон: {phone}\n"
            f"Сумма: {total_price} руб."
        )

        self.assertEqual(message, expected_message)
        self.assertEqual(len(buttons), 2)
        self.assertEqual(buttons[0][0]['text'], "✅ Подтвердить")
        self.assertEqual(buttons[1][0]['text'], "❌ Отклонить")

    def test_booking_message_with_missing_phone_and_price(self):
        service = "Студийная фотосессия"
        date = "2025-05-12"
        times = ["10:00", "12:00"]
        name = "Иван Иванов"
        phone = None
        total_price = 0

        with self.assertRaises(ValueError):
            booking_message_with_buttons(service, date, times, name, phone, total_price)

    def test_booking_message_with_empty_name(self):
        service = "Студийная фотосессия"
        date = "2025-05-12"
        times = ["10:00", "12:00"]
        name = ""
        phone = "+79991234567"
        total_price = 5000

        with self.assertRaises(ValueError):
            booking_message_with_buttons(service, date, times, name, phone, total_price)

    def test_booking_message_with_empty_phone(self):
        service = "Студийная фотосессия"
        date = "2025-05-12"
        times = ["10:00", "12:00"]
        name = "Иван Иванов"
        phone = ""
        total_price = 5000

        with self.assertRaises(ValueError):
            booking_message_with_buttons(service, date, times, name, phone, total_price)

    def test_booking_message_with_zero_price(self):
        service = "Студийная фотосессия"
        date = "2025-05-12"
        times = ["10:00", "12:00"]
        name = "Иван Иванов"
        phone = "+79991234567"
        total_price = 0

        with self.assertRaises(ValueError) as exc:
            booking_message_with_buttons(service, date, times, name, phone, total_price)
        assert "Цена должна быть больше 0" in str(exc.exception)

if __name__ == "__main__":
    unittest.main()
