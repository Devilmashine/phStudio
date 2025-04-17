# 🚀 Деплой фронта на Vercel/Netlify, бэкенда — на Render/Fly.io

## 1. Frontend (React) на Vercel

1. Зарегистрируйтесь на https://vercel.com
2. Импортируйте репозиторий (GitHub/GitLab/Bitbucket)
3. Vercel автоматически определит React-проект (Vite/CRA)
4. Укажите build command: `npm run build`, output: `dist`
5. Настройте переменные окружения (если нужно):
   - Например, `VITE_API_URL=https://your-backend-url/api/`
6. Деплойте — сайт будет доступен по адресу вида `https://your-project.vercel.app`
7. Для своего домена — добавьте CNAME/A-запись в панели Vercel

---

## 2. Frontend (React) на Netlify

1. Зарегистрируйтесь на https://netlify.com
2. Импортируйте репозиторий
3. Build command: `npm run build`, publish directory: `dist`
4. Настройте переменные окружения (если нужно)
5. Деплойте — сайт будет доступен по адресу вида `https://your-project.netlify.app`
6. Для своего домена — настройте CNAME/A-запись

---

## 3. Backend (FastAPI) на Render

1. Зарегистрируйтесь на https://render.com
2. Создайте новое Web Service, выберите репозиторий с backend
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host=0.0.0.0 --port=10000`
5. Укажите переменные окружения (секреты)
6. После деплоя API будет доступен по адресу вида `https://your-backend.onrender.com/api/`

---

## 4. Backend на Fly.io (альтернатива)

1. Зарегистрируйтесь на https://fly.io
2. Установите flyctl:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```
3. Инициализируйте приложение:
   ```bash
   fly launch
   ```
4. Настройте Dockerfile (если нужно)
5. Деплойте:
   ```bash
   fly deploy
   ```
6. Укажите переменные окружения через панель или `fly secrets set`

---

## 5. Ограничения
- Бесплатные тарифы могут "засыпать" (cold start)
- Лимиты по памяти, времени, количеству запросов
- Для production — рекомендуется платный тариф

---

## 6. Проверка
- Фронт доступен по домену Vercel/Netlify или вашему
- API доступен по Render/Fly.io
- Проверьте CORS и переменные окружения

---

**Если нужна помощь с настройкой build, переменных или домена — дай знать!** 