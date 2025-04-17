# 🛠️ Туториал для разработчиков

## 1. Быстрый старт

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/photo-studio-booking.git
   cd photo-studio-booking
   ```
2. Установите зависимости:
   - Frontend:
     ```bash
     npm install
     ```
   - Backend:
     ```bash
     cd backend
     pip install -r requirements.txt
     ```
3. Настройте переменные окружения (см. README.md).
4. Запустите backend:
   ```bash
   uvicorn backend.app.main:app --reload
   ```
5. Запустите frontend:
   ```bash
   npm run dev
   ```

---

## 2. Структура проекта

- `src/` — основной код фронта
- `backend/` — код backend (FastAPI)
- `docs/` — документация (API, туториалы)
- `tests/` — тесты (юнит, интеграционные)
- `.github/` — шаблоны для CI/CD, issue, pull request

---

## 3. Тестирование
- Backend: `pytest tests/`
- Frontend: `npm run test`
- Интеграционные тесты: используйте curl/Postman (см. API.md)

---

## 4. Добавление новых фич
- Соблюдайте структуру директорий и правила коммитов.
- Для новых API — обновляйте `docs/API.md`.
- Для новых сценариев — пишите тесты в `tests/`.
- Перед пушем — убедитесь, что все тесты проходят.

---

## 5. Советы
- Все секреты — только на сервере.
- Используйте линтеры (ESLint, Flake8).
- Следите за changelog и roadmap. 