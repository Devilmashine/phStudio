"""
Enhanced Cache Service with Redis integration and multi-layer caching.

This module provides a production-grade caching solution with:
- Multi-layer caching (L1 in-memory, L2 Redis)
- Distributed locking
- Cache invalidation strategies
- Performance optimization
- Fallback mechanisms
"""

import asyncio
import json
import pickle
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from functools import wraps
import hashlib

from .result import Result, success, failure, DomainError


class CacheError(DomainError):
    """Base class for cache-related errors."""
    pass


class CacheConnectionError(CacheError):
    """Error raised when cache connection fails."""
    
    def __init__(self, message: str):
        super().__init__(message, code="CACHE_CONNECTION_ERROR")


class CacheOperationError(CacheError):
    """Error raised when cache operation fails."""
    
    def __init__(self, message: str):
        super().__init__(message, code="CACHE_OPERATION_ERROR")


class LockAcquisitionError(CacheError):
    """Error raised when distributed lock cannot be acquired."""
    
    def __init__(self, message: str):
        super().__init__(message, code="LOCK_ACQUISITION_ERROR")


T = TypeVar('T')


class CacheStrategy:
    """
    Multi-layer caching implementation with fallback mechanisms.
    
    This class implements a sophisticated caching strategy that combines
    in-memory caching with Redis for optimal performance and scalability.
    """
    
    def __init__(self, redis_client=None, max_memory_size: int = 1000):
        self.l1_cache = MemoryCache(max_size=max_memory_size)
        self.l2_cache = RedisCache(redis_client) if redis_client else None
        self._lock = asyncio.Lock()
    
    async def get_with_fallback(
        self,
        key: str,
        loader: Callable[[], Any],
        ttl: int = 300,
        use_l2: bool = True
    ) -> Result[Any, CacheError]:
        """
        Multi-layer cache with fallback to source.
        
        Args:
            key: Cache key
            loader: Function to load data if not in cache
            ttl: Time to live in seconds
            use_l2: Whether to use L2 cache
            
        Returns:
            Cached value or loaded data
        """
        try:
            # Try L1 cache first
            value = self.l1_cache.get(key)
            if value is not None:
                return success(value)
            
            # Try L2 cache if available
            if use_l2 and self.l2_cache:
                value = await self.l2_cache.get(key)
                if value is not None:
                    # Update L1 cache with shorter TTL
                    self.l1_cache.set(key, value, ttl=60)
                    return success(value)
            
            # Load from source
            value = await loader()
            
            # Update both caches
            if use_l2 and self.l2_cache:
                await self.l2_cache.set(key, value, ttl=ttl)
            
            self.l1_cache.set(key, value, ttl=60)
            
            return success(value)
            
        except Exception as e:
            return failure(
                CacheOperationError(f"Cache operation failed: {str(e)}")
            )
    
    async def set_multi_layer(
        self,
        key: str,
        value: Any,
        ttl: int = 300
    ) -> Result[bool, CacheError]:
        """Set value in both L1 and L2 caches."""
        try:
            # Set in L1 cache
            self.l1_cache.set(key, value, ttl=60)
            
            # Set in L2 cache if available
            if self.l2_cache:
                await self.l2_cache.set(key, value, ttl=ttl)
            
            return success(True)
            
        except Exception as e:
            return failure(
                CacheOperationError(f"Failed to set cache: {str(e)}")
            )
    
    async def invalidate_multi_layer(self, key: str) -> Result[bool, CacheError]:
        """Invalidate key in both L1 and L2 caches."""
        try:
            # Invalidate in L1 cache
            self.l1_cache.delete(key)
            
            # Invalidate in L2 cache if available
            if self.l2_cache:
                await self.l2_cache.delete(key)
            
            return success(True)
            
        except Exception as e:
            return failure(
                CacheOperationError(f"Failed to invalidate cache: {str(e)}")
            )
    
    async def get_distributed_lock(
        self,
        lock_key: str,
        timeout: int = 10,
        ttl: int = 30
    ) -> Result['DistributedLock', CacheError]:
        """Acquire distributed lock."""
        if not self.l2_cache:
            return failure(
                CacheOperationError("Distributed locking requires L2 cache")
            )
        
        return await self.l2_cache.acquire_lock(lock_key, timeout, ttl)


class MemoryCache:
    """
    In-memory cache implementation with LRU eviction.
    
    This provides fast access to frequently used data with automatic
    memory management and eviction policies.
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._cache: Dict[str, '_CacheEntry'] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check if expired
        if entry.is_expired():
            del self._cache[key]
            self._access_order.remove(key)
            return None
        
        # Update access order
        self._access_order.remove(key)
        self._access_order.append(key)
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Set value in cache."""
        # Remove existing entry
        if key in self._cache:
            del self._cache[key]
            self._access_order.remove(key)
        
        # Create new entry
        entry = _CacheEntry(value, ttl)
        self._cache[key] = entry
        self._access_order.append(key)
        
        # Evict if necessary
        if len(self._cache) > self.max_size:
            self._evict_lru()
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]
            self._access_order.remove(key)
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": self._calculate_hit_rate(),
            "memory_usage": self._estimate_memory_usage()
        }
    
    def _evict_lru(self) -> None:
        """Evict least recently used entries."""
        while len(self._cache) > self.max_size:
            if self._access_order:
                oldest_key = self._access_order.pop(0)
                del self._cache[oldest_key]
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        # This would implement proper hit rate calculation
        return 0.0
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage in bytes."""
        # This would implement proper memory estimation
        return len(self._cache) * 1000  # Rough estimate


class RedisCache:
    """
    Redis cache implementation with advanced features.
    
    This provides distributed caching with Redis backend, including
    distributed locking, pub/sub, and advanced data structures.
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self._lock_prefix = "lock:"
        self._pubsub_prefix = "pubsub:"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache."""
        try:
            value = await self.redis.get(key)
            if value is None:
                return None
            
            # Try to deserialize
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Fallback to pickle for complex objects
                try:
                    return pickle.loads(value)
                except (pickle.PickleError, TypeError):
                    return value
                    
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in Redis cache."""
        try:
            # Try to serialize as JSON first
            try:
                serialized = json.dumps(value)
            except (TypeError, ValueError):
                # Fallback to pickle for complex objects
                serialized = pickle.dumps(value)
            
            await self.redis.setex(key, ttl, serialized)
            return True
            
        except Exception:
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        try:
            result = await self.redis.exists(key)
            return result > 0
        except Exception:
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key."""
        try:
            result = await self.redis.expire(key, ttl)
            return result > 0
        except Exception:
            return False
    
    async def ttl(self, key: str) -> int:
        """Get time to live for key."""
        try:
            result = await self.redis.ttl(key)
            return result
        except Exception:
            return -1
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in Redis."""
        try:
            result = await self.redis.incrby(key, amount)
            return result
        except Exception:
            return None
    
    async def acquire_lock(
        self,
        lock_key: str,
        timeout: int = 10,
        ttl: int = 30
    ) -> Result['DistributedLock', CacheError]:
        """Acquire distributed lock."""
        try:
            lock = DistributedLock(self.redis, f"{self._lock_prefix}{lock_key}", ttl)
            acquired = await lock.acquire(timeout)
            
            if acquired:
                return success(lock)
            else:
                return failure(
                    LockAcquisitionError(f"Failed to acquire lock: {lock_key}")
                )
                
        except Exception as e:
            return failure(
                CacheOperationError(f"Lock acquisition failed: {str(e)}")
            )
    
    async def publish(self, channel: str, message: Any) -> bool:
        """Publish message to Redis channel."""
        try:
            serialized = json.dumps(message)
            result = await self.redis.publish(f"{self._pubsub_prefix}{channel}", serialized)
            return result > 0
        except Exception:
            return False
    
    async def subscribe(self, channel: str) -> 'RedisSubscription':
        """Subscribe to Redis channel."""
        try:
            subscription = RedisSubscription(self.redis, f"{self._pubsub_prefix}{channel}")
            return subscription
        except Exception:
            return None


class CacheService:
    """
    Main cache service that provides a unified interface for caching operations.
    
    This class provides a simple interface that can be used throughout the application
    for caching operations, with fallback to in-memory cache if Redis is not available.
    """
    
    def __init__(self, redis_client=None, max_memory_size: int = 1000):
        self.cache_strategy = CacheStrategy(redis_client, max_memory_size)
        self._initialized = False
    
    async def initialize(self):
        """Initialize the cache service."""
        self._initialized = True
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._initialized:
            await self.initialize()
        
        # Simple get from L1 cache for now
        return self.cache_strategy.l1_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache."""
        if not self._initialized:
            await self.initialize()
        
        self.cache_strategy.l1_cache.set(key, value, ttl)
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._initialized:
            await self.initialize()
        
        return self.cache_strategy.l1_cache.delete(key)
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        if not self._initialized:
            await self.initialize()
        
        self.cache_strategy.l1_cache.clear()
    
    async def get_with_loader(
        self,
        key: str,
        loader: Callable[[], Any],
        ttl: int = 300
    ) -> Any:
        """Get value from cache or load using loader function."""
        if not self._initialized:
            await self.initialize()
        
        result = await self.cache_strategy.get_with_fallback(key, loader, ttl)
        if result.is_success():
            return result.value
        raise Exception(f"Cache operation failed: {result.error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache_strategy.l1_cache.get_stats()


class _CacheEntry:
    """Internal cache entry with expiration."""
    
    def __init__(self, value: Any, ttl: int):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() - self.created_at > self.ttl


class DistributedLock:
    """
    Distributed lock implementation using Redis.
    
    This provides reliable distributed locking for coordinating
    operations across multiple application instances.
    """
    
    def __init__(self, redis_client, lock_key: str, ttl: int = 30):
        self.redis = redis_client
        self.lock_key = lock_key
        self.ttl = ttl
        self._acquired = False
        self._lock_value = None
        self._refresh_task = None
    
    async def acquire(self, timeout: int = 10) -> bool:
        """
        Acquire the lock.
        
        Args:
            timeout: Maximum time to wait for lock acquisition
            
        Returns:
            True if lock acquired, False otherwise
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Generate unique lock value
            self._lock_value = f"{time.time()}:{id(self)}"
            
            # Try to acquire lock
            result = await self.redis.set(
                self.lock_key,
                self._lock_value,
                ex=self.ttl,
                nx=True  # Only set if not exists
            )
            
            if result:
                self._acquired = True
                # Start refresh task
                self._start_refresh_task()
                return True
            
            # Wait before retry
            await asyncio.sleep(0.1)
        
        return False
    
    async def release(self) -> bool:
        """Release the lock."""
        if not self._acquired:
            return False
        
        try:
            # Stop refresh task
            if self._refresh_task:
                self._refresh_task.cancel()
                try:
                    await self._refresh_task
                except asyncio.CancelledError:
                    pass
            
            # Release lock using Lua script for atomicity
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = await self.redis.eval(
                lua_script,
                1,
                self.lock_key,
                self._lock_value
            )
            
            self._acquired = False
            return result > 0
            
        except Exception:
            return False
    
    def _start_refresh_task(self) -> None:
        """Start task to refresh lock TTL."""
        async def refresh_lock():
            while self._acquired:
                try:
                    await asyncio.sleep(self.ttl // 3)  # Refresh every 1/3 of TTL
                    if self._acquired:
                        await self.redis.expire(self.lock_key, self.ttl)
                except asyncio.CancelledError:
                    break
                except Exception:
                    # If refresh fails, assume lock is lost
                    self._acquired = False
                    break
        
        self._refresh_task = asyncio.create_task(refresh_lock())
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.release()


class RedisSubscription:
    """Redis pub/sub subscription."""
    
    def __init__(self, redis_client, channel: str):
        self.redis = redis_client
        self.channel = channel
        self.pubsub = None
    
    async def subscribe(self):
        """Subscribe to channel."""
        try:
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe(self.channel)
        except Exception:
            pass
    
    async def listen(self):
        """Listen for messages."""
        if not self.pubsub:
            await self.subscribe()
        
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        yield data
                    except (json.JSONDecodeError, TypeError):
                        yield message["data"]
        except Exception:
            pass
    
    async def unsubscribe(self):
        """Unsubscribe from channel."""
        if self.pubsub:
            await self.pubsub.unsubscribe(self.channel)
            await self.pubsub.close()


# Cache decorators and utilities
def cached(
    ttl: int = 300,
    key_prefix: str = "",
    use_l2: bool = True,
    cache_service: Optional[CacheStrategy] = None
):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Cache TTL in seconds
        key_prefix: Prefix for cache keys
        use_l2: Whether to use L2 cache
        cache_service: Cache service instance
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache_service:
                return await func(*args, **kwargs)
            
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add args and kwargs to key
            if args:
                key_parts.extend([str(arg) for arg in args])
            if kwargs:
                for k, v in sorted(kwargs.items()):
                    key_parts.extend([k, str(v)])
            
            cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            result = await cache_service.get_with_fallback(
                cache_key,
                lambda: func(*args, **kwargs),
                ttl=ttl,
                use_l2=use_l2
            )
            
            if result.is_success():
                return result.value
            else:
                # Fallback to direct execution
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def cache_invalidate(
    pattern: str,
    cache_service: Optional[CacheStrategy] = None
):
    """
    Decorator for invalidating cache after function execution.
    
    Args:
        pattern: Cache key pattern to invalidate
        cache_service: Cache service instance
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if cache_service:
                # Invalidate cache based on pattern
                await cache_service.invalidate_multi_layer(pattern)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_cache_service: Optional[CacheStrategy] = None


def get_cache_service() -> Optional[CacheStrategy]:
    """Get global cache service instance."""
    return _cache_service


def set_cache_service(cache_service: CacheStrategy) -> None:
    """Set global cache service instance."""
    global _cache_service
    _cache_service = cache_service


# Convenience functions
async def get_cached(
    key: str,
    loader: Callable[[], Any],
    ttl: int = 300
) -> Result[Any, CacheError]:
    """Get cached value with fallback to loader."""
    cache_service = get_cache_service()
    if not cache_service:
        return failure(
            CacheError("No cache service configured")
        )
    
    return await cache_service.get_with_fallback(key, loader, ttl)


async def set_cached(
    key: str,
    value: Any,
    ttl: int = 300
) -> Result[bool, CacheError]:
    """Set value in cache."""
    cache_service = get_cache_service()
    if not cache_service:
        return failure(
            CacheError("No cache service configured")
        )
    
    return await cache_service.set_multi_layer(key, value, ttl)


async def delete_cached(key: str) -> Result[bool, CacheError]:
    """Delete key from cache."""
    cache_service = get_cache_service()
    if not cache_service:
        return failure(
            CacheError("No cache service configured")
        )
    
    return await cache_service.invalidate_multi_layer(key)


async def acquire_lock(
    lock_key: str,
    timeout: int = 10,
    ttl: int = 30
) -> Result[DistributedLock, CacheError]:
    """Acquire distributed lock."""
    cache_service = get_cache_service()
    if not cache_service:
        return failure(
            CacheError("No cache service configured")
        )
    
    return await cache_service.get_distributed_lock(lock_key, timeout, ttl)
