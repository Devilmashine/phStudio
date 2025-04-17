# 📚 API Документация

## Общие сведения
Все запросы к API осуществляются через backend (FastAPI). Формат данных — JSON. Аутентификация не требуется (для MVP).

---

## Эндпоинты

### 1. Получить доступные слоты
```
GET /api/calendar/events?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```
**Ответ:**
```json
[
  {
    "id": "event_id",
    "date": "2025-04-18",
    "times": ["10:00", "11:00"],
    "status": "confirmed"
  }
]
```

### 2. Создать бронирование
```
POST /api/bookings
```
**Тело запроса:**
```json
{
  "date": "2025-04-18",
  "times": ["10:00", "11:00"],
  "name": "Иван",
  "phone": "79999999999",
  "totalPrice": 5000
}
```
**Ответ:**
```json
{
  "success": true,
  "bookingId": "abc123"
}
```

### 3. Webhook для Telegram
```
POST /api/telegram/webhook
```
**Используется Telegram Bot API для обработки inline-кнопок.**

---

## Ошибки
- 400 — Неверный формат данных
- 409 — Слот уже занят
- 500 — Внутренняя ошибка сервера

---

## Примечания
- Все даты в формате YYYY-MM-DD
- Все операции с календарём — только через backend 