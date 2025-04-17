# 🚀 Деплой на Heroku

## 1. Backend (FastAPI)

1. Зарегистрируйтесь на https://heroku.com и установите Heroku CLI:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```
2. Войдите в аккаунт:
   ```bash
   heroku login
   ```
3. Перейдите в папку backend:
   ```bash
   cd backend
   ```
4. Создайте Procfile:
   ```
   web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-5000}
   ```
5. Создайте приложение:
   ```bash
   heroku create your-backend-app
   ```
6. Добавьте переменные окружения (секреты):
   ```bash
   heroku config:set GOOGLE_CALENDAR_ID=... GOOGLE_CLIENT_EMAIL=... GOOGLE_PRIVATE_KEY=... TELEGRAM_BOT_TOKEN=... TELEGRAM_CHAT_ID=...
   ```
7. Задеплойте код:
   ```bash
   git push heroku main
   # или если отдельный репозиторий для backend:
   git push heroku master
   ```
8. Проверьте логи:
   ```bash
   heroku logs --tail
   ```

---

## 2. Frontend (React)

### Вариант 1: Отдельное приложение на Heroku
1. Перейдите в папку frontend:
   ```bash
   cd frontend
   ```
2. Создайте Procfile:
   ```
   web: npm run build && npx serve -s dist -l $PORT
   ```
3. Создайте приложение:
   ```bash
   heroku create your-frontend-app
   ```
4. Деплойте код:
   ```bash
   git push heroku main
   ```

### Вариант 2: Статика на Vercel/Netlify (см. отдельный гайд)

---

## 3. Настройка домена и HTTPS
- В панели Heroku добавьте свой домен и следуйте инструкции для CNAME/A-записи.
- HTTPS предоставляется автоматически.

---

## 4. Ограничения Heroku Free
- Приложения могут "засыпать" (cold start).
- Лимиты по памяти и времени выполнения.
- Для production рекомендуется платный план.

---

## 5. Проверка
- Backend: https://your-backend-app.herokuapp.com/api/
- Frontend: https://your-frontend-app.herokuapp.com/

---

**Если нужна помощь с Procfile, настройкой buildpack или переменных — дай знать!** 