# 🚀 Локальный запуск (без Docker)

## ВАЖНО
- После запуска обязательно проверьте API с people_count (curl/Postman).
- Все переменные окружения и примеры должны содержать people_count, если это требуется для тестов/миграций.
- Перед запуском убедитесь, что все тесты (backend + frontend) проходят без ошибок и предупреждений.
- Документация и PROJECT_PLAN.md должны быть актуальны.

## Быстрый старт
1. Установите Python 3.10+, Node.js, npm, PostgreSQL.
2. В корне проекта создайте .env (см. README.md). Пример:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   ...
   # обязательно: people_count=2 (или другое положительное число)
   ```
3. Установите зависимости:
   ```bash
   pip install -r backend/requirements.txt
   npm install
   ```
4. Примените миграции:
   ```bash
   alembic upgrade head
   ```
5. Запустите backend и frontend:
   ```bash
   cd backend && uvicorn app.main:app --reload
   # в новом окне:
   cd frontend && npm run dev
   ```
6. Проверьте:
   - Фронт: http://localhost:5173/
   - API: http://localhost:8000/api/

## CI/CD
- Перед деплоем убедитесь, что все тесты проходят (npm test, pytest).
- Используйте GitHub Actions/Docker для автоматизации.

## Безопасность
- Все секреты — только в .env или переменных окружения.
- Не храните секреты в репозитории.

## Финальный чеклист для production-ready запуска
- [x] Все тесты (backend + frontend) проходят
- [x] people_count и другие обязательные поля присутствуют в .env и тестах
- [x] Документация и инструкции актуальны
- [x] Секреты не попадают в git
- [x] Проверена работоспособность API и UI после запуска