# 🚀 Локальный запуск для разработки и тестирования

## 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/photo-studio-booking.git
cd photo-studio-booking
```

---

## 2. Установка зависимостей

### Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend (React)
```bash
cd ../frontend
npm install
```

---

## 3. Настройка переменных окружения
- Создайте `.env` в корне проекта (см. README.md)
- Для frontend можно создать `frontend/.env` (например, VITE_API_URL)

---

## 4. Запуск

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

---

## 5. Проверка
- Фронт: http://localhost:5173/
- API: http://localhost:8000/api/

---

## 6. Тестирование
- Backend: `pytest tests/`
- Frontend: `npm run test`

---

## 7. Типичные ошибки
- Проверьте, что все переменные окружения заданы
- Проверьте, что backend и frontend используют одинаковый API_URL
- Если порт занят — измените его в настройках

---

**Если возникнут вопросы по локальному запуску — пиши!** 