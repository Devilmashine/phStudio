import logging

logger = logging.getLogger(__name__)

# Шаблон сообщения для Telegram (только с кнопками, без дублирования)
def booking_message_with_buttons(service, date, times, name, phone, total_price):
    logger.info(f"Получены данные: service={service}, date={date}, times={times}, name={name}, phone={phone}, total_price={total_price}")
    # Явная строгая валидация всех параметров
    if not service or not isinstance(service, str) or not service.strip():
        logger.error("Параметр 'service' обязателен и должен быть строкой")
        raise ValueError("Параметр 'service' обязателен и должен быть строкой")
    if not date or not isinstance(date, str) or not date.strip():
        logger.error("Параметр 'date' обязателен и должен быть строкой")
        raise ValueError("Параметр 'date' обязателен и должен быть строкой")
    if not times or not isinstance(times, (list, tuple)) or not all(isinstance(t, str) and t.strip() for t in times):
        logger.error(f"Параметр 'times' обязателен и должен быть списком строк, получено: {times}")
        raise ValueError("Параметр 'times' обязателен и должен быть списком строк и не пустым")
    if not name or not isinstance(name, str) or not name.strip():
        logger.error("Имя клиента обязательно и должно быть строкой")
        raise ValueError("Имя клиента обязательно и должно быть строкой")
    if not phone or not isinstance(phone, str) or not phone.strip():
        logger.error("Телефон клиента обязателен и должен быть строкой")
        raise ValueError("Телефон клиента обязателен и должен быть строкой")
    try:
        price_val = int(total_price)
    except Exception as e:
        logger.error(f"Ошибка преобразования total_price: {total_price}, ошибка: {e}")
        raise ValueError(f"Некорректная цена: {total_price}, ошибка: {e}")
    if price_val <= 0:
        logger.error(f"Цена должна быть больше 0, получено: {total_price}")
        raise ValueError("Цена должна быть больше 0")
    price_str = f"{price_val} руб."
    phone = phone if phone else 'Не указан'
    logger.debug(f"Обновленные данные: phone={phone}, total_price={price_str}")
    message = (
        f"🎨 Новое бронирование:\n"
        f"Услуга: {service}\n"
        f"Дата: {date}\n"
        f"Время: {', '.join(times)}\n"
        f"Клиент: {name}\n"
        f"Телефон: {phone}\n"
        f"Сумма: {price_str}"
    )
    buttons = [
        [{"text": "✅ Подтвердить", "callback_data": "confirm"}],
        [{"text": "❌ Отклонить", "callback_data": "reject"}]
    ]
    logger.info(f"Сформированное сообщение: {message}")
    return message, buttons