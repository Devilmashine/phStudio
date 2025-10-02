# Production Deployment Guide
# Руководство по развёртыванию в production

## 0. Что даст это руководство

Документ объясняет «по шагам» как развернуть Photo Studio CRM на арендованном сервере (VPS/выделенный). Текст рассчитан на новичка: все команды приведены полностью, рядом указано зачем они нужны и как проверить результат. После прохождения всех шагов у вас будет:

- настроенный сервер с Docker и Docker Compose;
- склонированный проект со всеми файлами конфигурации;
- запущенные контейнеры (PostgreSQL, Redis, backend, frontend, Celery, nginx, мониторинг);
- доступ по доменному имени по HTTPS;
- базовые задания по резервному копированию, обновлению и мониторингу.

## 1. Что подготовить заранее

### 1.1. Доступы и учётные данные
- Аккаунт у хостинг-провайдера и оплата сервера.
- SSH-доступ (обычно приходит на email: IP, логин `root`, пароль или приватный ключ).
- Доменное имя, которым будете пользоваться (например, `crm.myphotostudio.ru`).

### 1.2. Минимальные характеристики сервера
- 4 CPU, 8 ГБ RAM, 100 ГБ SSD — комфортный старт. Если мониторинг пока не нужен, можно 2 CPU и 4 ГБ RAM.
- Операционная система: Ubuntu 22.04 LTS (рекомендуем из-за поддержки и репозиториев). Команды ниже написаны для Ubuntu/Debian. Для CentOS/RHEL используйте `yum`/`dnf` аналоги.

### 1.3. Сетевая подготовка
- Откройте порты 22 (SSH), 80 (HTTP), 443 (HTTPS) в панели управления хостера.
- Настройте DNS-запись типа **A** на ваш IP (обычно в панели регистратора домена). Пример: `crm.myphotostudio.ru → 203.0.113.10`.

## 2. Подключение к серверу и базовая конфигурация

> Выполняйте команды поочерёдно. После ввода пароля в SSH символы не отображаются — это нормально.

1. Подключитесь по SSH:
   ```bash
   ssh root@203.0.113.10
   ```
2. Обновите систему и установите важные утилиты:
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y curl git ufw jq
   ```
3. Настройте часовой пояс (меняйте на свой регион):
   ```bash
   sudo timedatectl set-timezone Europe/Moscow
   sudo timedatectl status
   ```
4. Создайте отдельного пользователя для приложения (так безопаснее):
   ```bash
   sudo adduser phstudio
   sudo usermod -aG sudo phstudio
   sudo usermod -aG docker phstudio || true  # добавим позже, после установки Docker
   ```
5. Настройте SSH-доступ для нового пользователя (используйте новую сессию, не разрывая текущую):
   ```bash
   rsync --archive --chown=phstudio:phstudio ~/.ssh /home/phstudio
   ```
6. Проверка: выйдите (`exit`) и подключитесь снова уже как `phstudio`.

## 3. Установка Docker и Docker Compose

1. Установите Docker официальным скриптом:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```
2. Добавьте пользователя в группу docker и активируйте изменения (нужен relogin):
   ```bash
   sudo usermod -aG docker phstudio
   newgrp docker
   docker --version
   ```
3. Установите Docker Compose v2 как плагин:
   ```bash
   sudo apt install -y docker-compose-plugin
   docker compose version
   ```
4. Включите автозапуск службы Docker:
   ```bash
   sudo systemctl enable docker
   sudo systemctl start docker
   sudo systemctl status docker
   ```

## 4. Настройка файрвола (UFW)

1. Разрешите SSH, HTTP, HTTPS:
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   sudo ufw status
   ```
2. Если соединение прервалось — подключитесь снова, всё работает.

## 5. Получение проекта на сервер

1. Выберите каталог, где будет лежать код. Часто используют `/opt`:
   ```bash
   sudo mkdir -p /opt/phstudio
   sudo chown phstudio:phstudio /opt/phstudio
   cd /opt/phstudio
   ```
2. Клонируйте репозиторий (замените ссылку, если используете свой форк или приватный Git):
   ```bash
   git clone https://github.com/your-username/phstudio-crm.git
   cd phstudio-crm
   ```
3. Проверьте содержимое:
   ```bash
   ls
   ```
   Убедитесь, что есть файлы `docker-compose.prod.yml`, каталоги `backend`, `frontend`, `nginx` и др.

## 6. Подготовка переменных окружения

1. Скопируйте шаблон:
   ```bash
   cp .env.example .env.production
   ```
2. Откройте файл любым редактором (например, `nano`):
   ```bash
   nano .env.production
   ```
3. Заполните значения (пример):
   ```env
   POSTGRES_DB=phstudio_crm
   POSTGRES_USER=phstudio_user
   POSTGRES_PASSWORD=SuperSecretPassword123

   REDIS_PASSWORD=AnotherSecret123

   SECRET_KEY=$(openssl rand -hex 32)
   JWT_SECRET_KEY=$(openssl rand -hex 32)

   CORS_ORIGINS=https://crm.myphotostudio.ru

   GRAFANA_PASSWORD=GrafanaAdminPass123

   REACT_APP_API_URL=https://crm.myphotostudio.ru
   REACT_APP_WS_URL=wss://crm.myphotostudio.ru
   ```
   > Советы: пароли не должны содержать пробелов; для генерации используйте `openssl rand -hex 32`. Если не планируете мониторинг, можно временно убрать строки с Grafana.
4. Сохраните файл (`Ctrl+O`, `Enter`, `Ctrl+X`).
5. Проверьте, что файл не попадёт в Git:
   ```bash
   git status
   ```
   `.env.production` должен отображаться как «Untracked». Не добавляйте его в коммиты.

## 7. Настройка SSL-сертификата (Let's Encrypt)

1. Установите certbot (для standalone режима):
   ```bash
   sudo apt install -y certbot
   ```
2. Освободите порты 80/443 (на случай, если ранее что-то слушает их):
   ```bash
   sudo systemctl stop nginx || true
   ```
3. Выпустите сертификат, указав домен:
   ```bash
   sudo certbot certonly --standalone -d crm.myphotostudio.ru
   ```
   Сертификаты попадут в `/etc/letsencrypt/live/crm.myphotostudio.ru/`.
4. Создайте каталог для сертификатов проекта и скопируйте файлы:
   ```bash
   mkdir -p nginx/ssl
   sudo cp /etc/letsencrypt/live/crm.myphotostudio.ru/fullchain.pem nginx/ssl/
   sudo cp /etc/letsencrypt/live/crm.myphotostudio.ru/privkey.pem nginx/ssl/
   sudo chown phstudio:phstudio nginx/ssl/*.pem
   ```
5. Для автоматического обновления добавьте cron-задание:
   ```bash
   sudo crontab -e
   ```
   Добавьте строку:
   ```
   0 3 * * * certbot renew --quiet && docker compose -f /opt/phstudio/phstudio-crm/docker-compose.prod.yml exec nginx nginx -s reload
   ```
   Это проверит сертификаты каждую ночь и перезагрузит nginx при обновлении.

## 8. Проверка конфигурации nginx

1. Откройте `nginx/nginx.prod.conf` и убедитесь, что указаны пути к сертификатам:
   ```bash
   nano nginx/nginx.prod.conf
   ```
   В блоке `ssl_certificate` должны использоваться файлы из `nginx/ssl`. Если требуется изменить домен или upstream — сделайте это сейчас.
2. При необходимости добавьте редиректы с HTTP на HTTPS (обычно уже настроено в файле). Сохраните изменения.

## 9. Первый запуск Docker Compose

1. Проверьте, что находитесь в каталоге проекта `/opt/phstudio/phstudio-crm`.
2. Выполните сборку и запуск:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
3. Проследите за логами, пока сервисы стартуют (может занять 1–3 минуты):
   ```bash
   docker compose -f docker-compose.prod.yml logs -f backend
   ```
   Остановите просмотр `Ctrl+C`.
4. Убедитесь, что все контейнеры в состоянии `Up`:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   ```

## 10. Проверка доступности

1. Локальные проверки с сервера:
   ```bash
   curl -f http://localhost/health
   curl -f http://localhost:8000/health
   ```
2. Проверка из браузера: откройте `https://crm.myphotostudio.ru`. Должна появиться авторизационная форма.
3. Если страница недоступна:
   - проверьте DNS (команда `dig crm.myphotostudio.ru`);
   - убедитесь, что сертификаты скопированы верно;
   - просмотрите логи nginx и backend:
     ```bash
     docker compose -f docker-compose.prod.yml logs -f nginx
     docker compose -f docker-compose.prod.yml logs -f backend
     ```

## 11. Настройка автозапуска контейнеров

- Docker уже настроен на автозапуск. Контейнеры имеют политику `restart: unless-stopped`, поэтому после перезагрузки сервера они запустятся автоматически.
- Для ручного управления используйте:
  ```bash
  docker compose -f docker-compose.prod.yml restart
  docker compose -f docker-compose.prod.yml stop
  docker compose -f docker-compose.prod.yml start
  ```

## 12. Обновление приложения

### 12.1. Ручное обновление
1. Перейдите в каталог проекта:
   ```bash
   cd /opt/phstudio/phstudio-crm
   ```
2. Получите свежие изменения:
   ```bash
   git pull origin main
   ```
3. Пересоберите и перезапустите контейнеры:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
4. При необходимости выполните миграции (если проект их требует):
   ```bash
   docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
   ```

### 12.2. Автоматизация через CI/CD
- Настройте GitHub Actions/другую CI-систему, которая по пушу в `main` будет подключаться по SSH и выполнять шаги выше.
- В `Actions secrets` добавьте: `DOCKER_USERNAME`, `DOCKER_PASSWORD`, `PRODUCTION_HOST`, `PRODUCTION_USER`, `PRODUCTION_SSH_KEY`.

## 13. Резервное копирование

1. Создайте каталог для бэкапов:
   ```bash
   mkdir -p /opt/backups
   ```
2. Создайте скрипт `/opt/phstudio/phstudio-crm/scripts/backup.sh`:
   ```bash
   cat <<'EOF' > scripts/backup.sh
   #!/bin/bash
   set -e
   DATE=$(date +%Y%m%d_%H%M%S)
   DEST="/opt/backups/phstudio_$DATE"
   mkdir -p "$DEST"

   docker compose -f /opt/phstudio/phstudio-crm/docker-compose.prod.yml exec postgres pg_dump -U phstudio_user phstudio_crm > "$DEST/database.sql"
   rsync -a /opt/phstudio/phstudio-crm/backend/uploads "$DEST/uploads"
   cp /opt/phstudio/phstudio-crm/.env.production "$DEST/.env.production"
   echo "Backup created at $DEST"
   EOF
   chmod +x scripts/backup.sh
   ```
3. Добавьте cron-задание для ежедневного бэкапа:
   ```bash
   crontab -e
   ```
   Добавьте строку:
   ```
   30 2 * * * /opt/phstudio/phstudio-crm/scripts/backup.sh >> /opt/backups/backup.log 2>&1
   ```
4. Храните бэкапы на внешнем диске или облаке, чтобы восстановиться при аварии.

## 14. Мониторинг и логирование

- **Grafana** (панели мониторинга): `https://crm.myphotostudio.ru:3001`, логин `admin`, пароль — из `.env.production` (`GRAFANA_PASSWORD`).
- **Prometheus** (метрики): `https://crm.myphotostudio.ru:9090`.
- **Loki** (агрегатор логов) + **Promtail** (отправляет логи) уже настроены и собирают данные.
- Чтобы смотреть логи в терминале:
  ```bash
  docker compose -f docker-compose.prod.yml logs -f
  docker compose -f docker-compose.prod.yml logs -f backend
  ```
- Если ресурсы сервера ограничены и мониторинг не нужен, закомментируйте блоки `prometheus`, `grafana`, `loki`, `promtail` в `docker-compose.prod.yml` перед запуском.

## 15. Диагностика проблем

| Ситуация | Что проверить |
| --- | --- |
| Сайт не открывается | DNS, статус контейнеров `docker compose ps`, логи nginx `docker compose logs -f nginx` |
| Backend не отвечает | `docker compose logs -f backend`, проверить подключение к БД (переменные `POSTGRES_*`) |
| База данных не стартует | Правильность паролей, отсутствие старых данных в томе `postgres_data` |
| Certbot не обновляет сертификат | Посмотреть `/var/log/letsencrypt/letsencrypt.log`, проверить cron (`systemctl status cron`) |
| Нехватает места | `df -h`, удалить старые образы `docker system prune -af`, чистить логи в `/opt/backups`, `nginx/logs` |

## 16. Масштабирование (когда серверу тесно)

- Увеличьте количество экземпляров backend или celery:
  ```bash
  docker compose -f docker-compose.prod.yml up -d --scale backend=3 --scale celery_worker=3
  ```
- При росте нагрузки подготовьте отдельный балансировщик (например, внешний nginx/HAProxy) и разнесите БД на выделенный сервер.

## 17. Правила безопасности

- Регулярно ставьте обновления:
  ```bash
  sudo apt update && sudo apt upgrade -y
  docker compose -f docker-compose.prod.yml pull
  ```
- Меняйте пароли от админок, не храните их в открытом виде.
- Ограничьте SSH-доступ используя ключи и fail2ban (при необходимости установите `sudo apt install fail2ban`).
- Не забудьте про обновление сертификатов (cron выше).

## 18. Полезные команды (шпаргалка)

```bash
# Статус всех сервисов
docker compose -f docker-compose.prod.yml ps

# Войти в контейнер backend
docker compose -f docker-compose.prod.yml exec backend bash

# Проверить работоспособность API
curl -f https://crm.myphotostudio.ru/health

# Проверить использование ресурсов Docker
docker stats

# Остановить все сервисы
docker compose -f docker-compose.prod.yml down
```

## 19. Дальнейшие шаги и поддержка

- Создайте отдельный staging-сервер, где будете тестировать обновления.
- Следите за issue-трекером проекта, обновляйте зависимости.
- При необходимости обращайтесь: `support@phstudio.com`, Telegram `@phstudio_support`, GitHub Issues.

---

**Помните:** перед изменениями и обновлениями делайте бэкапы и проверяйте всё на staging. Это сэкономит время и нервы при работе в production.
