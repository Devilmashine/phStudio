# 🚀 Деплой через Docker Compose (универсально)

## Введение
Этот гайд подходит для любого Linux/Windows/Mac сервера, локального ПК или облака. Используется Docker Compose для одновременного запуска backend (FastAPI) и frontend (React).

---

## 1. Установка Docker и docker-compose

- [Инструкция для Linux](https://docs.docker.com/engine/install/)
- [Инструкция для Windows/Mac](https://docs.docker.com/desktop/)

Проверьте:
```bash
docker --version
docker-compose --version
```

---

## 2. Структура docker-compose.yml

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    env_file:
      - .env
    ports:
      - "8000:8000"
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
  frontend:
    build: ./frontend
    environment:
      - VITE_API_URL=http://localhost:8000/api/
    ports:
      - "5173:80"
    command: ["npx", "serve", "-s", "dist", "-l", "80"]
```

---

## 3. Настройка переменных окружения
- Создайте `.env` в корне (см. README.md)
- Для frontend можно добавить переменные в `frontend/.env`

---

## 4. Сборка и запуск
```bash
docker-compose up -d --build
```

---

## 5. Проверка
- Фронт: http://localhost:5173/
- API: http://localhost:8000/api/

---

## 6. Обновление
```bash
git pull
docker-compose up -d --build
```

---

## 7. Безопасность
- Не храните секреты в публичных репозиториях
- Открывайте только нужные порты
- Для production — настройте HTTPS через nginx/caddy

---

**Если нужен готовый docker-compose.yml под твой проект — дай знать!** 