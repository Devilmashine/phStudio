# REST API

Корневой URL по умолчанию — `http://localhost:8000/api`.

## Аутентификация

Большинство административных эндпоинтов требуют Bearer-token с ролью `admin` или `manager`.

### POST `/auth/login`
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin@example.com",
  "password": "password"
}
```

Успешный ответ:
```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Используйте токен в заголовке `Authorization: Bearer <JWT>`.

## Бронирования

### GET `/bookings?skip=0&limit=100`
Возвращает список бронирований (для сотрудников/админов).

### GET `/bookings/{booking_id}`
Возвращает бронирование по идентификатору. 404, если не найдено.

### POST `/bookings/public/`
Публичное создание бронирования без авторизации.

Пример тела:
```json
{
  "date": "2025-09-29",
  "start_time": "2025-09-29T19:00:00+03:00",
  "end_time": "2025-09-29T21:00:00+03:00",
  "total_price": 5000,
  "client_name": "Иван",
  "client_phone": "+79999999999",
  "people_count": 2
}
```

Ошибки:
- `409 Conflict` — слот пересекается с существующим бронированием;
- `400/422` — некорректные данные (датчики, people_count и т.д.).

### PATCH `/bookings/{booking_id}/status`
Изменение статуса бронирования (`pending`, `confirmed`, `cancelled`, `completed`). Требует авторизации сотрудника.

## Календарь

### GET `/calendar/month-availability?year=2025&month=9`
Возвращает агрегацию по дням месяца.

Ответ:
```json
{
  "2025-09-29": {
    "available_slots": 10,
    "total_slots": 12,
    "booked_slots": 2
  }
}
```

### GET `/calendar/day-details?date=2025-09-29`
Возвращает список часовых интервалов и флаг `available`.

## Calendar events

Эндпоинты `calendar-events` предназначены для управляемого календаря (администратор).

- `GET /calendar-events?start_date=2025-09-01&end_date=2025-09-30`
- `POST /calendar-events/`
- `PUT /calendar-events/{id}`
- `DELETE /calendar-events/{id}`

### Пример создания события
```json
{
  "title": "Fashion-съёмка",
  "description": "Съёмка lookbook",
  "start_time": "2025-09-29T19:00:00+03:00",
  "end_time": "2025-09-29T21:00:00+03:00",
  "people_count": 6,
  "status": "pending"
}
```

## Telegram интеграция

### POST `/telegram/webhook`
Принимает сообщения от Telegram-бота. Тело соответствует документации Telegram. Ответ всегда `{ "status": "ok" }` при успешном приёме.

## Studio settings

- `GET /settings/` — получить текущие настройки (admin/manager).
- `POST /settings/` — создать набор настроек, если отсутствует.
- `PUT /settings/` — обновить параметры (рабочие дни, тарифы, уведомления).

Пример ответа:
```json
{
  "work_days": ["mon", "tue", "wed", "thu", "fri"],
  "work_start_time": "09:00",
  "work_end_time": "20:00",
  "base_price_per_hour": 2500,
  "weekend_price_multiplier": 1.5,
  "holidays": ["2025-01-01"],
  "min_booking_duration": 1,
  "max_booking_duration": 8,
  "advance_booking_days": 30
}
```

## Коды ошибок
- `400 Bad Request` — неверные данные;
- `401 Unauthorized` / `403 Forbidden` — отсутствует токен или недостаточно прав;
- `404 Not Found` — объект не найден;
- `409 Conflict` — слот пересекается или занят;
- `422 Unprocessable Entity` — не пройдена валидация Pydantic;
- `500 Internal Server Error` — непредвиденная ошибка сервера.

## Инструменты ручного тестирования

Используйте curl или Postman. Пример запроса:
```bash
curl -X POST http://localhost:8000/api/bookings/public/ \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-09-29",
    "start_time": "2025-09-29T19:00:00+03:00",
    "end_time": "2025-09-29T21:00:00+03:00",
    "total_price": 5000,
    "client_name": "Test",
    "client_phone": "+79999999999",
    "people_count": 2
  }'
```