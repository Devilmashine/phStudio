# 🚀 Деплой на Heroku

## ВАЖНО
- После деплоя обязательно проверьте API с people_count (curl/Postman).

## Backend (FastAPI)
1. Зарегистрируйтесь на https://heroku.com и установите Heroku CLI.
2. Перейдите в папку backend:
   ```bash
   cd backend
   ```
3. Создайте Procfile:
   ```
   web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-5000}
   ```
4. Создайте приложение и добавьте переменные окружения (секреты, people_count обязателен в API).
5. Задеплойте код:
   ```bash
   git push heroku main
   ```
6. Проверьте логи:
   ```bash
   heroku logs --tail
   ```

## Frontend (React)
- Соберите фронт: `npm run build`, загрузите в Netlify/Vercel или используйте отдельный Heroku app с build командой.

## CI/CD
- Перед деплоем убедитесь, что все тесты проходят (npm test, pytest).

## Безопасность
- Все секреты — только в .env или переменных окружения.

---

**Если нужна помощь с Procfile, настройкой buildpack или переменных — дай знать!**