from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis.asyncio as redis
import os
from datetime import timedelta
import json
from typing import Any, Dict, List

# Время жизни кэша для разных типов данных
CACHE_TTL = {
    'calendar_state': 300,  # 5 минут для состояния календаря
    'settings': 3600,      # 1 час для настроек
    'gallery': 1800        # 30 минут для галереи
}

async def setup_cache():
    """Инициализация кэша с Redis"""
    redis_instance = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis_instance), prefix="phstudio-cache:")

def cache_key_builder(
    func,
    namespace: str = "",
    *args: Any,
    **kwargs: Any,
) -> str:
    """Построитель ключей кэша с учетом параметров запроса"""
    kwargs_key = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return f"{namespace}:{func.__module__}:{func.__name__}:{kwargs_key}"

# Декоратор для кэширования состояния календаря
def cache_calendar_state(namespace: str = "calendar"):
    return cache(
        expire=CACHE_TTL['calendar_state'],
        namespace=namespace,
        key_builder=cache_key_builder
    )

# Декоратор для кэширования настроек
def cache_settings(namespace: str = "settings"):
    return cache(
        expire=CACHE_TTL['settings'],
        namespace=namespace,
        key_builder=cache_key_builder
    )

# Декоратор для кэширования галереи
def cache_gallery(namespace: str = "gallery"):
    return cache(
        expire=CACHE_TTL['gallery'],
        namespace=namespace,
        key_builder=cache_key_builder
    )

async def invalidate_calendar_cache():
    """Инвалидация кэша календаря при изменениях"""
    redis_instance = await FastAPICache.get_backend()
    pattern = "phstudio-cache:calendar:*"
    keys = await redis_instance.keys(pattern)
    if keys:
        await redis_instance.delete(*keys)
