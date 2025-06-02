# 🚀 Деплой на Vercel/Netlify (Frontend)

## ВАЖНО
- После деплоя обязательно проверьте интеграцию с backend и API с people_count (curl/Postman).
- Все переменные окружения и примеры должны содержать people_count, если это требуется для тестов/миграций.
- Перед деплоем убедитесь, что все тесты (frontend + backend) проходят без ошибок и предупреждений.
- Документация и PROJECT_PLAN.md должны быть актуальны.

## Быстрый старт
1. Зарегистрируйтесь на Vercel/Netlify и создайте проект.
2. Настройте переменные окружения (Environment Variables) в настройках проекта. Пример:
   ```env
   VITE_API_URL=https://your-backend-url/api
   ...
   # обязательно: people_count=2 (или другое положительное число)
   ```
3. Загрузите код frontend (git push, drag&drop).
4. Проверьте:
   - Фронт: https://your-app.vercel.app/ или https://your-app.netlify.app/
   - API: https://your-backend-url/api/

## CI/CD
- Перед деплоем убедитесь, что все тесты проходят (npm test, pytest).
- Используйте GitHub Actions/Docker для автоматизации.

## Безопасность
- Все секреты — только в Environment Variables/переменных окружения.
- Не храните секреты в репозитории.

## Финальный чеклист для production-ready деплоя
- [x] Все тесты (frontend + backend) проходят
- [x] people_count и другие обязательные поля присутствуют в Environment Variables и тестах
- [x] Документация и инструкции актуальны
- [x] Секреты не попадают в git
- [x] Проверена работоспособность API и UI после деплоя