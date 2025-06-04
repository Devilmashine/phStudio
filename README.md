# 📸 Система Бронирования Фотостудии

## ВАЖНО
- people_count обязателен для всех бронирований и событий календаря (frontend, backend, API, тесты).
- Вся документация, примеры и тесты приведены к единому формату (см. ниже).
- Фронтенд находится в src/ (React, TypeScript), запуск npm install и npm run dev — из корня проекта.

## Архитектура
- **Frontend**: React + TypeScript (src/)
- **Backend**: FastAPI (backend/)
- **Интеграции**: Google Calendar, Telegram Bot
- **CI/CD**: GitHub Actions (юнит-тесты, линтинг)

## Быстрый старт
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/photo-studio-booking.git
   cd photo-studio-booking
   ```
2. Установите зависимости:
   - Фронтенд (в корне):
     ```bash
     npm install
     ```
   - Бэкенд:
     ```bash
     cd backend
     pip install -r requirements.txt
     ```
3. Настройте переменные окружения (см. ниже).
4. Запустите backend:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
5. Запустите frontend:
   ```bash
   npm run dev
   ```

## Пример .env
```
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_CLIENT_EMAIL=your_service_account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
```

## Пример запроса бронирования (API)
```json
{
  "date": "2025-04-18",
  "times": ["10:00", "11:00"],
  "name": "Иван",
  "phone": "79999999999",
  "total_price": 5000,
  "people_count": 2
}
```

## Тестирование
- Backend: `pytest tests/`
- Frontend: `npm run test`
- Интеграционные тесты: curl/Postman (см. docs/API.md)

## Безопасность
- Все секреты — только в .env или переменных окружения.
- JWT-токен содержит роль пользователя, сверяется при каждом запросе.

## CI/CD
- Все тесты и линт обязательны для успешного деплоя.
- Ошибки тестов блокируют деплой.

## Структура проекта
- `src/` — фронтенд (React, TypeScript)
- `backend/` — backend (FastAPI)
- `docs/` — документация (API, туториалы, деплой)
- `tests/` — тесты (юнит, интеграция)
- `.github/` — CI/CD

## Советы
- Для новых API и сценариев — обновляйте docs/API.md и тесты.
- Все тесты должны проходить перед пушем.
- Все секреты — только на сервере.
- Используйте линтеры (ESLint, Flake8).
- Следите за changelog и roadmap.

## Финальный статус (Июнь 2025)

- Проект переведён на собственную систему календаря и полноценную БД (PostgreSQL)
- Все CRUD, сервисы, роуты и валидация реализованы и синхронизированы (backend + frontend)
- Все тесты (backend + frontend) проходят, предупреждения устранены
- Раздел "Настройки студии" (часы работы, цены, тех. перерывы) реализован и протестирован
- Личный кабинет: дашборд бронирований, настройки студии, защищённый доступ по ролям, тесты
- Документация и инструкции по деплою полностью актуализированы
- Система готова к эксплуатации и масштабированию

## Рекомендации

- После каждого крупного обновления — запускать полный прогон тестов (pytest, npm test)
- Документацию и PROJECT_PLAN.md поддерживать в актуальном состоянии
- Для деплоя использовать инструкции из docs/DEPLOY_*.md
- Все секреты и переменные окружения — только на сервере
- Для CI/CD использовать GitHub Actions/Docker

---
