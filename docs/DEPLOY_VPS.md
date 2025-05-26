# 🚀 Деплой на VPS (reg.ru, Hetzner, DigitalOcean, Yandex Cloud и др.)

## ВАЖНО
- После деплоя обязательно проверьте API с people_count (curl/Postman).

## Быстрый старт
1. Установите Docker и docker-compose.
2. Клонируйте проект и создайте .env (см. README.md).
3. Запустите:
   ```bash
   docker-compose up -d --build
   ```
4. Проверьте:
   - Фронт: http://your_server_ip:5173/
   - API: http://your_server_ip:8000/api/

## CI/CD
- Перед деплоем убедитесь, что все тесты проходят (npm test, pytest).

## Безопасность
- Все секреты — только в .env или переменных окружения.