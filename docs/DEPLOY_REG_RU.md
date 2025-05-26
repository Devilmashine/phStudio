# 🚀 Деплой на reg.ru (shared hosting)

## ВАЖНО
- После деплоя обязательно проверьте API с people_count (curl/Postman).

## Быстрый старт
1. Соберите production-версию фронта:
   ```bash
   npm run build
   ```
   В каталоге `dist/` появятся статические файлы.
2. Загрузите содержимое `dist/` в папку `public_html` вашего хостинга (через FTP или файловый менеджер reg.ru).
3. Загрузите папку `backend/` на сервер (через FTP/SFTP).
4. Создайте виртуальное окружение Python и установите зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r backend/requirements.txt
   ```
5. Создайте .env (см. README.md) вне public_html.
6. Настройте запуск FastAPI через uvicorn или WSGI/ASGI (см. панель reg.ru).

## CI/CD
- Перед деплоем убедитесь, что все тесты проходят (npm test, pytest).

## Безопасность
- Все секреты — только в .env или переменных окружения (НЕ класть в public_html).