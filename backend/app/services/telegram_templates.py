# Шаблоны сообщений для Telegram

def booking_message_template(service, date, times, name, phone, total_price):
    return (
        f"🎨 Новое бронирование:\n"
        f"Услуга: {service}\n"
        f"Дата: {date}\n"
        f"Время: {', '.join(times)}\n"
        f"Клиент: {name}\n"
        f"Телефон: {phone}\n"
        f"Сумма: {total_price} руб."
    )

def confirmation_message_template(booking_id, client_name, date, time):
    return (
        f"✅ Бронирование подтверждено\n\n"
        f"🆔 ID: {booking_id}\n"
        f"👤 Клиент: {client_name}\n"
        f"📅 Дата: {date}\n"
        f"🕒 Время: {time}\n"
    )

def cancellation_message_template(booking_id, client_name, reason=None):
    msg = (
        f"❌ Бронирование отменено\n\n"
        f"🆔 ID: {booking_id}\n"
        f"👤 Клиент: {client_name}\n"
    )
    if reason:
        msg += f"\n📝 Причина отмены:\n{reason}"
    return msg 