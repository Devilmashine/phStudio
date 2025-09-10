# Production Deployment Guide
# Руководство по развертыванию в production

## 🚀 Обзор

Это руководство описывает процесс развертывания Photo Studio CRM в production среде с использованием Docker, мониторинга и автоматизации.

## 📋 Предварительные требования

### Системные требования
- **CPU**: 4+ cores
- **RAM**: 8GB+ 
- **Storage**: 100GB+ SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+

### Программное обеспечение
- Docker 20.10+
- Docker Compose 2.0+
- Git
- curl/wget

### Сетевые требования
- Открытые порты: 80, 443, 22
- SSL сертификаты (Let's Encrypt рекомендуется)
- Домен или IP адрес

## 🔧 Подготовка сервера

### 1. Обновление системы
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 2. Установка Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# CentOS/RHEL
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
```

### 3. Установка Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🔐 Настройка безопасности

### 1. Создание пользователя для приложения
```bash
sudo useradd -m -s /bin/bash phstudio
sudo usermod -aG docker phstudio
```

### 2. Настройка файрвола
```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 3. Настройка SSL сертификатов
```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d your-domain.com
```

## 📁 Развертывание приложения

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/phstudio-crm.git
cd phstudio-crm
```

### 2. Создание переменных окружения
```bash
cp .env.example .env.production
```

Отредактируйте `.env.production`:
```env
# Database
POSTGRES_DB=phstudio_crm
POSTGRES_USER=phstudio_user
POSTGRES_PASSWORD=your_secure_password

# Redis
REDIS_PASSWORD=your_redis_password

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here

# CORS
CORS_ORIGINS=https://your-domain.com

# Monitoring
GRAFANA_PASSWORD=your_grafana_password

# Sentry (optional)
SENTRY_DSN=your_sentry_dsn
REACT_APP_SENTRY_DSN=your_sentry_dsn

# API URLs
REACT_APP_API_URL=https://your-domain.com
REACT_APP_WS_URL=wss://your-domain.com
```

### 3. Запуск приложения
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps
```

## 📊 Мониторинг и логирование

### 1. Доступ к мониторингу
- **Grafana**: https://your-domain.com:3001
- **Prometheus**: https://your-domain.com:9090
- **Loki**: https://your-domain.com:3100

### 2. Настройка алертов
```bash
# Копирование конфигурации алертов
cp monitoring/alert_rules.yml /var/lib/prometheus/
```

### 3. Просмотр логов
```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f backend
```

## 🔄 Обновление приложения

### 1. Автоматическое обновление (CI/CD)
```bash
# Настройка GitHub Actions secrets
# - DOCKER_USERNAME
# - DOCKER_PASSWORD
# - PRODUCTION_HOST
# - PRODUCTION_USER
# - PRODUCTION_SSH_KEY
```

### 2. Ручное обновление
```bash
# Остановка сервисов
docker-compose -f docker-compose.prod.yml down

# Обновление кода
git pull origin main

# Пересборка и запуск
docker-compose -f docker-compose.prod.yml up -d --build
```

## 🛠️ Обслуживание

### 1. Резервное копирование
```bash
# Создание скрипта бэкапа
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/phstudio_$DATE"

mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U phstudio_user phstudio_crm > $BACKUP_DIR/database.sql

# Uploads backup
cp -r ./backend/uploads $BACKUP_DIR/

# Configuration backup
cp .env.production $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh
```

### 2. Очистка логов
```bash
# Очистка старых логов
find ./logs -name "*.log" -mtime +30 -delete

# Очистка Docker логов
docker system prune -f
```

### 3. Мониторинг ресурсов
```bash
# Использование диска
df -h

# Использование памяти
free -h

# Docker статистика
docker stats
```

## 🚨 Устранение неполадок

### 1. Проверка здоровья сервисов
```bash
# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Проверка логов
docker-compose -f docker-compose.prod.yml logs backend
```

### 2. Перезапуск сервисов
```bash
# Перезапуск конкретного сервиса
docker-compose -f docker-compose.prod.yml restart backend

# Перезапуск всех сервисов
docker-compose -f docker-compose.prod.yml restart
```

### 3. Восстановление из бэкапа
```bash
# Остановка сервисов
docker-compose -f docker-compose.prod.yml down

# Восстановление базы данных
docker-compose -f docker-compose.prod.yml up -d postgres
sleep 10
docker-compose -f docker-compose.prod.yml exec postgres psql -U phstudio_user -d phstudio_crm < /backups/database.sql

# Запуск всех сервисов
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Масштабирование

### 1. Горизонтальное масштабирование
```bash
# Увеличение количества backend инстансов
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### 2. Настройка load balancer
```bash
# Обновление nginx конфигурации
# Добавление upstream серверов
```

## 🔒 Безопасность

### 1. Регулярные обновления
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker-compose -f docker-compose.prod.yml pull
```

### 2. Security audit
```bash
# Запуск security audit
./scripts/security-audit.sh
```

### 3. Мониторинг безопасности
- Регулярная проверка логов на подозрительную активность
- Мониторинг неудачных попыток входа
- Обновление SSL сертификатов

## 📞 Поддержка

### Контакты
- **Email**: support@phstudio.com
- **Telegram**: @phstudio_support
- **GitHub Issues**: [Создать issue](https://github.com/your-username/phstudio-crm/issues)

### Полезные команды
```bash
# Проверка статуса всех сервисов
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов в реальном времени
docker-compose -f docker-compose.prod.yml logs -f

# Проверка использования ресурсов
docker stats

# Проверка здоровья приложения
curl -f https://your-domain.com/health
```

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Важно**: Всегда тестируйте изменения в staging среде перед развертыванием в production!
