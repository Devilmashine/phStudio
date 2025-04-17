# 🚀 Деплой в Яндекс.Облако (Yandex Cloud)

## Вариант 1: Compute Cloud (виртуальная машина)

1. Создайте ВМ в Yandex Cloud (Ubuntu 22.04, 2+ ГБ RAM).
2. Подключитесь по SSH:
   ```bash
   ssh yc-user@your_vm_ip
   ```
3. Установите Docker и docker-compose (см. DEPLOY_VPS.md).
4. Клонируйте проект, настройте .env, запустите через docker-compose.
5. Настройте A-запись домена на внешний IP ВМ.
6. Для HTTPS используйте Let's Encrypt (certbot) или Caddy.

---

## Вариант 2: Serverless (Cloud Functions)

- Backend можно развернуть как Cloud Function (FastAPI через ASGI adapter, например, Mangum или serverless-wsgi).
- Фронтенд — как статику в Object Storage (см. ниже).
- Ограничения: нет постоянного состояния, лимиты по времени выполнения.

**Пример деплоя фронта:**

1. Соберите фронт:
   ```bash
   npm run build
   ```
2. Загрузите содержимое `dist/` в Yandex Object Storage (через web-интерфейс или s3cmd):
   ```bash
   s3cmd put --recursive dist/ s3://your-bucket-name/
   ```
3. Включите статический хостинг для бакета.
4. Привяжите домен через CNAME.

---

## Вариант 3: Backend на Yandex Cloud Functions

1. Упакуйте backend как serverless-приложение (FastAPI + Mangum).
2. Загрузите код через web-интерфейс или CLI.
3. Настройте endpoint и переменные окружения.
4. Ограничения: нет WebSocket, лимиты по времени и памяти.

---

## Примечания
- Для production лучше использовать Compute Cloud (ВМ) или Managed Service for Kubernetes.
- Для статики — Object Storage (дёшево и быстро).
- Для serverless — только если нет сложных интеграций и WebSocket.

---

**Если нужна помощь с docker-compose, Cloud Functions или Object Storage — дай знать!** 