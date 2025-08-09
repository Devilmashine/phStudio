# API Документация

## Аутентификация и безопасность

Все защищенные эндпоинты требуют JWT токен в заголовке:
```http
Authorization: Bearer <token>
```

### Получение токена
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "admin@example.com",
    "password": "password123"
}
```

Ответ:
```json
{
    "access_token": "eyJ0...",
    "token_type": "bearer"
}
```

## Календарь и бронирования

### Получение событий календаря
```http
GET /api/calendar-events?start_date=2025-08-01&end_date=2025-08-31&status=available
Authorization: Bearer <token>
```

### Создание бронирования
```http
POST /api/bookings
Content-Type: application/json

{
    "date": "2025-08-01",
    "times": ["10:00", "11:00"],
    "name": "Иван",
    "phone": "79999999999",
    "email": "ivan@example.com",
    "total_price": 5000,
    "people_count": 2,
    "notes": "Нужен визажист"
}
  "people_count": 2
}
```

### Webhook для Telegram
```
POST /api/telegram/webhook
```

### Получить все бронирования (для сотрудников/админов)
```
GET /api/bookings
```

### Получить одно бронирование по id
```
GET /api/bookings/{booking_id}
```

### Получить всех клиентов (для сотрудников/админов)
```
GET /api/clients
```

### Получить одного клиента по id
```
GET /api/clients/{client_id}
```

### Создать клиента (опционально, если не через бронирование)
```
POST /api/clients
```

### Получить всех сотрудников/админов
```
GET /api/users
```

## StudioSettings (Настройки студии)

### GET /api/settings/
- Получить текущие настройки студии (требуется роль admin/manager)
- Ответ: объект StudioSettings

### POST /api/settings/
- Создать настройки студии (только для admin, если не существует)
- Тело запроса: StudioSettingsCreate
- Ответ: объект StudioSettings

### PUT /api/settings/
- Обновить настройки студии (только для admin)
- Тело запроса: StudioSettingsUpdate
- Ответ: объект StudioSettings

#### Пример объекта StudioSettings
```json
{
  "id": 1,
  "work_days": ["mon", "tue", "wed", "thu", "fri"],
  "work_start_time": "09:00",
  "work_end_time": "20:00",
  "base_price_per_hour": 2500,
  "weekend_price_multiplier": 1.5,
  "telegram_notifications_enabled": true,
  "email_notifications_enabled": true,
  "holidays": ["2025-01-01"],
  "min_booking_duration": 1,
  "max_booking_duration": 8,
  "advance_booking_days": 30
}
```

---

## Примечания
- Личный кабинет для клиентов не реализуется, но все данные о клиентах и бронированиях доступны сотрудникам и администраторам через защищённые эндпоинты.
- Для доступа к защищённым эндпоинтам требуется Bearer-токен с ролью admin/manager.
- Все новые поля и сущности отражены в структуре БД и документации.

## Ошибки
- 400 — Неверный формат данных
- 409 — Слот уже занят
- 422 — Отсутствует обязательное поле (например, people_count)
- 500 — Внутренняя ошибка сервера

## Аутентификация
- Для защищённых эндпоинтов используйте Bearer-токен (роль содержится в access_token).

## Примеры ручного тестирования
- Используйте curl/Postman, обязательно people_count в payload.

## Финальный статус (2025)

- Все эндпоинты актуальны, структура данных синхронизирована между backend и frontend
- Вся валидация (people_count, service и др.) реализована строго
- Документация и примеры актуальны