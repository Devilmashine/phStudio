# 🚀 Деплой фронта на Vercel/Netlify, бэкенда — на Render/Fly.io

## ВАЖНО
- После деплоя обязательно проверьте API с people_count (curl/Postman).

## Frontend (React) на Vercel/Netlify
- Импортируйте репозиторий, build command: `npm run build`, output: `dist`.
- Настройте переменные окружения (например, `VITE_API_URL`).
- После деплоя сайт будет доступен по адресу вида `https://your-project.vercel.app` или `https://your-project.netlify.app`.

## Backend (FastAPI) на Render/Fly.io
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host=0.0.0.0 --port=10000`
- Укажите переменные окружения (секреты, people_count обязателен в API).

## CI/CD
- Перед деплоем убедитесь, что все тесты проходят (npm test, pytest).

## Безопасность
- Все секреты — только в .env или переменных окружения.