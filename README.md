# 📸 Система Бронирования Фотостудии

## 🚀 Обзор Проекта
Модульная система для онлайн-бронирования фотостудии с интеграцией Google Calendar и Telegram, поддержкой подтверждения/отклонения брони через Telegram-кнопки, безопасной архитектурой и продвинутым UX.

---

## 🏗️ Архитектура
- **Frontend**: React + TypeScript + TailwindCSS (Vite)
- **Backend**: FastAPI (Python 3.10+), Google Calendar API, Telegram Bot API
- **Интеграции**:
  - Google Calendar (через сервисный аккаунт, только на бэкенде)
  - Telegram Bot (уведомления, inline-кнопки для админов)
- **CI/CD**: GitHub Actions (юнит-тесты, линтинг)
- **Мониторинг**: Sentry (готово к интеграции)

---

## 🌟 Ключевые Возможности
- 📅 Интерактивное бронирование с реальным календарём
- 🕒 Гибкое управление слотами времени
- 🤖 Telegram-уведомления с inline-кнопками (подтвердить/отклонить)
- 🔒 Безопасное хранение секретов (только на бэкенде)
- 🌐 Синхронизация с Google Calendar
- 🛡️ Валидация и защита от ошибок
- 🧩 Готовность к масштабированию и кастомизации

---

## 📦 Требования
- Node.js (v18+)
- Python 3.10+
- npm или yarn
- Google Cloud Project (сервисный аккаунт, Calendar API)
- Telegram Bot (токен, chat_id группы)

---

## 🔧 Быстрый старт

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/your-username/photo-studio-booking.git
cd photo-studio-booking
```

2. **Установите зависимости**
```bash
npm install
cd backend
pip install -r requirements.txt
```

3. **Настройте переменные окружения**
Создайте `.env` в корне:
```
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_CLIENT_EMAIL=your_service_account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=-1001234567890
```

4. **Запустите backend**
```bash
uvicorn backend.app.main:app --reload
```

5. **Запустите frontend**
```bash
npm run dev
```

---

## 📝 Интеграция с Google Calendar
- Все ключи и ID хранятся только на бэкенде.
- Сервисный аккаунт должен быть добавлен в календарь с правами "Редактор".
- Все операции с календарём идут через backend API.

## 🤖 Интеграция с Telegram
- Бот добавлен в админ-группу.
- При каждом бронировании в группу отправляется сообщение с inline-кнопками:
  - "✅ Подтвердить" — обновляет статус, редактирует сообщение, может уведомлять клиента.
  - "❌ Отклонить" — аналогично, с возможностью указать причину.
- Webhook для Telegram: `/api/telegram/webhook` (установить через BotFather или curl).

---

## 🔒 Безопасность
- Все секреты только на сервере.
- Фронт не содержит ни одного токена или ключа.
- Валидация данных на всех слоях.
- Защита от XSS/CSRF (CORS, sanitization).

---

## 🧪 Тестирование
- Backend: `pytest tests/`
- Frontend: `npm run test`
- Интеграционные тесты: curl/Postman примеры в разделе API.

---

## 🚢 CI/CD
- Линтинг и тесты запускаются при каждом push/pull request (GitHub Actions).
- Dockerfile и docker-compose для быстрого деплоя.

---

## 📚 Примеры API

### Создать бронирование (POST)
```
POST /api/bookings
{
  "date": "2025-04-18",
  "times": ["10:00", "11:00"],
  "name": "Иван",
  "phone": "79999999999",
  "totalPrice": 5000
}
```

### Получить события календаря (GET)
```
GET /api/calendar/events?start_date=2025-04-18&end_date=2025-04-19
```

---

## 🗺️ Дорожная карта
- [x] Интеграция с Google Calendar
- [x] Интеграция с Telegram (уведомления, inline-кнопки)
- [x] Безопасное хранение секретов
- [x] Подтверждение/отклонение брони через Telegram
- [ ] Мобильная версия
- [ ] Расширенная аналитика
- [ ] Интеграция платежей

---

## 🛡️ Best Practices
- Все ключи и токены — только на сервере.
- Любая логика подтверждения/отклонения — только через backend.
- Все внешние интеграции — через отдельные сервисы/модули.
- Мониторинг ошибок через Sentry (готово к интеграции).
- Покрытие тестами всех критических путей.

---

## 📄 Лицензия
MIT License

---

**Создано с ❤️ для профессиональных фотостудий**
