# 🚀 Деплой в Яндекс.Облако (Yandex Cloud)

## ВАЖНО
- После деплоя обязательно проверьте API с people_count (curl/Postman).

## Быстрый старт (Compute Cloud)
1. Создайте ВМ в Yandex Cloud (Ubuntu 22.04, 2+ ГБ RAM).
2. Установите Docker и docker-compose.
3. Клонируйте проект и создайте .env (см. README.md).
4. Запустите:
   ```bash
   docker-compose up -d --build
   ```
5. Проверьте:
   - Фронт: http://your_vm_ip:5173/
   - API: http://your_vm_ip:8000/api/

## CI/CD
- Перед деплоем убедитесь, что все тесты проходят (npm test, pytest).

## Безопасность
- Все секреты — только в .env или переменных окружения.

## Альтернативы
- Для serverless и Object Storage — см. оригинальный гайд, people_count обязателен во всех payload.