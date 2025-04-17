# 🚀 Деплой на VPS (reg.ru, Hetzner, DigitalOcean, Yandex Cloud и др.)

## Введение
Этот гайд описывает развертывание проекта на любом VPS с root-доступом (Ubuntu/Debian/CentOS). Используется Docker и docker-compose для простоты и надёжности.

---

## 1. Подготовка сервера

1. Закажите VPS (любой провайдер: reg.ru, Hetzner, DigitalOcean, Yandex Cloud и др.).
2. Подключитесь по SSH:
   ```bash
   ssh user@your_server_ip
   ```
3. Обновите систему:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

## 2. Установка Docker и docker-compose

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Перелогиньтесь или выполните:
su - $USER
# Установите docker-compose (если не входит в docker):
sudo apt install docker-compose -y
```

---

## 3. Клонирование проекта

```bash
git clone https://github.com/your-username/photo-studio-booking.git
cd photo-studio-booking
```

---

## 4. Настройка переменных окружения

1. Создайте файл `.env` в корне проекта:
   ```
   GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
   GOOGLE_CLIENT_EMAIL=your_service_account@project.iam.gserviceaccount.com
   GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=-1001234567890
   ```
2. (Опционально) настройте переменные для frontend (например, API_URL).

---

## 5. Запуск через Docker Compose

1. Проверьте, что в проекте есть `docker-compose.yml` (если нет — создай или попроси меня).
2. Запустите:
   ```bash
   docker-compose up -d --build
   ```
3. Проверьте логи:
   ```bash
   docker-compose logs -f
   ```

---

## 6. Настройка домена и HTTPS

1. Настройте A-запись домена на IP VPS.
2. Для HTTPS используйте [Caddy](https://caddyserver.com/) или [Let's Encrypt](https://letsencrypt.org/) (через nginx/certbot).
3. Пример для nginx:
   - Установите nginx: `sudo apt install nginx`
   - Настройте проксирование на backend/frontend (пример конфига — в README.md или по запросу).

---

## 7. Обновление проекта

```bash
git pull
docker-compose up -d --build
```

---

## 8. Безопасность
- Не храните секреты в публичных репозиториях.
- Откройте только нужные порты (обычно 80, 443).
- Используйте firewall (ufw).

---

## 9. Проверка
- Фронт доступен по домену/IP
- API работает по `/api/`
- Логи ошибок: `docker-compose logs`

---

**Если нужна помощь с docker-compose.yml или nginx — дай знать!** 