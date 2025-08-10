import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi import Request
import os
from dotenv import load_dotenv

load_dotenv()

# Настройки Redis для rate limiting
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))


async def setup_rate_limiter():
    """Инициализация rate limiter с Redis"""
    redis_instance = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
    )
    await FastAPILimiter.init(redis_instance)


# Декоратор для ограничения запросов
# 100 запросов в минуту для обычных endpoints
default_rate_limit = RateLimiter(times=100, seconds=60)

# 20 запросов в минуту для авторизации
auth_rate_limit = RateLimiter(times=20, seconds=60)

# 200 запросов в минуту для получения данных календаря
calendar_rate_limit = RateLimiter(times=200, seconds=60)


async def get_client_ip(request: Request) -> str:
    """Получение IP клиента с учетом прокси"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host
