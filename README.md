# 📸 Photo Studio Booking Platform

Модульная система бронирования фотостудии с публичным фронтендом и административным API.

## Основные возможности
- бронирование в часовом поясе Europe/Moscow (UTC+3) с блокировкой занятых и прошедших слотов;
- актуальное отображение календаря и детальной доступности по дням;
- поддержка Telegram-уведомлений о новых бронированиях;
- миграции и модели на FastAPI + SQLAlchemy;
- frontend на React + TypeScript + Vite.

## Требования
- Node.js ≥ 20
- npm ≥ 9
- Python ≥ 3.10
- PostgreSQL 14+ (для production)

## Быстрый старт
```bash
git clone https://github.com/Devilmashine/phStudio.git
cd phStudio

# Frontend
npm ci
npm run dev

# Backend (в отдельном терминале)
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

По умолчанию frontend доступен на <http://localhost:5173>, backend — на <http://localhost:8000>.

## Переменные окружения
Создайте файл `.env` в корне `backend/` со значениями, соответствующими вашему окружению.

| Ключ | Назначение |
| --- | --- |
| `DATABASE_URL` | строка подключения к PostgreSQL |
| `SECRET_KEY` | секрет FastAPI для подписи JWT |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | параметры Telegram-бота (опционально) |
| `MAX_BOOKING_DAYS_AHEAD`, `MIN_BOOKING_HOURS` | ограничения бронирования |

## Тестирование и контроль качества
```bash
# Backend (использует in-memory SQLite)
PYTHONPATH=backend pytest tests/test_optimizations.py -v

# Frontend
npm run lint
npm run build
```

## CI/CD
GitHub Actions предоставляет два workflow:
- **CI** (`.github/workflows/ci.yml`) — запускается на push/pull request, выполняет
  - установку python-зависимостей и pytest для `tests/test_optimizations.py`;
  - установку npm-зависимостей, eslint и production build фронтенда.
- **Docker Build & Push** (`.github/workflows/deploy.yml`) — при push в `main` или ручном запуске строит и публикует docker-образы backend/frontend в GHCR.

## Структура каталогов
```
backend/   – FastAPI приложение, миграции Alembic, сервисы
frontend/  – React/Vite клиент
docs/      – техническая документация (API)
tests/     – объединённые pytest сценарии
.github/   – конфигурация GitHub Actions
```

## Документация
- `docs/API.md` — актуальные REST-эндпоинты (аутентификация, бронирования, календарь)
- `CHANGELOG.md` — хронология значимых изменений

## Развёртывание
Для production-релиза используйте готовые Dockerfile (`backend/Dockerfile.prod`, `frontend/Dockerfile.prod`). Workflow `Docker Build & Push` собирает и публикует образы `ghcr.io/<owner>/phStudio-frontend` и `phStudio-backend`.

## Поддержка
- перед коммитом запускайте lint и тесты;
- не храните секреты в репозитории; используйте `.env` и GitHub Secrets;
- актуализируйте документацию и changelog при функциональных изменениях.
- `FIXES_APPLIED.md` — примененные исправления
- `GITHUB_ACTIONS_FIXES.md` — исправления GitHub Actions
- `LEGAL_COMPLIANCE_IMPLEMENTATION_REPORT.md` — отчет о соблюдении законодательства
- `SECURITY_AUDIT_REPORT.md` — отчет по безопасности
- `SECURITY_IMPLEMENTATION_FINAL_REPORT.md` — финальный отчет по безопасности
- `TELEGRAM_REFACTOR_REPORT.md` — отчет о рефакторинге Telegram

## Советы
- Для новых API и сценариев — обновляйте docs/API.md и тесты.
- Все тесты должны проходить перед пушем.
- Все секреты — только на сервере.
- Используйте линтеры (ESLint, Flake8).
- Следите за changelog и roadmap.

## Рекомендации

- После каждого крупного обновления — запускать полный прогон тестов (pytest, npm test)
- Документацию и PROJECT_PLAN.md поддерживать в актуальном состоянии
- Для деплоя использовать инструкции из docs/DEPLOY_*.md
- Все секреты и переменные окружения — только на сервере
- Для CI/CD использовать GitHub Actions/Docker

---
