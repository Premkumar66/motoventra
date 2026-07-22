"""
MotoMod AI — Redis Cache Client
Async Redis with type-safe get/set and cache invalidation patterns
"""
import json
from typing import Any, Optional
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

# ─── Redis Client Singleton ───────────────────────────────────────────────────

_redis_client: Optional[Redis] = None


async def get_redis_client() -> Redis:
    """Return or create the global Redis async client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5,
        )
        logger.info("redis_client_initialized", url=settings.REDIS_URL)
    return _redis_client


async def close_redis_client() -> None:
    """Close the Redis client connection pool."""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("redis_client_closed")


async def check_redis_connection() -> bool:
    """Health check for Redis connectivity."""
    try:
        client = await get_redis_client()
        await client.ping()
        return True
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        return False


# ─── Cache Manager ───────────────────────────────────────────────────────────

class CacheManager:
    """High-level Redis cache manager with JSON serialization."""

    def __init__(self, prefix: str = "motomod"):
        self.prefix = prefix

    def _make_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached value. Returns None on miss or error."""
        try:
            client = await get_redis_client()
            raw = await client.get(self._make_key(key))
            if raw is None:
                return None
            return json.loads(raw)
        except RedisError as e:
            logger.warning("cache_get_error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = settings.CACHE_TTL_SECONDS,
    ) -> bool:
        """Store a value in cache with TTL in seconds."""
        try:
            client = await get_redis_client()
            serialized = json.dumps(value, default=str)
            await client.setex(self._make_key(key), ttl, serialized)
            return True
        except RedisError as e:
            logger.warning("cache_set_error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Remove a key from cache."""
        try:
            client = await get_redis_client()
            await client.delete(self._make_key(key))
            return True
        except RedisError as e:
            logger.warning("cache_delete_error", key=key, error=str(e))
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern. Returns count deleted."""
        try:
            client = await get_redis_client()
            full_pattern = self._make_key(pattern)
            keys = [key async for key in client.scan_iter(full_pattern)]
            if keys:
                return await client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning("cache_delete_pattern_error", pattern=pattern, error=str(e))
            return 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            client = await get_redis_client()
            return bool(await client.exists(self._make_key(key)))
        except RedisError:
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Atomically increment a counter."""
        try:
            client = await get_redis_client()
            return await client.incrby(self._make_key(key), amount)
        except RedisError:
            return None

    async def get_ttl(self, key: str) -> int:
        """Return remaining TTL in seconds for a key (-1 if no TTL, -2 if not exists)."""
        try:
            client = await get_redis_client()
            return await client.ttl(self._make_key(key))
        except RedisError:
            return -2


# ─── Named Cache Instances ────────────────────────────────────────────────────

bike_cache = CacheManager(prefix="motomod:bikes")
prediction_cache = CacheManager(prefix="motomod:predictions")
user_cache = CacheManager(prefix="motomod:users")
search_cache = CacheManager(prefix="motomod:search")
rate_limit_cache = CacheManager(prefix="motomod:rate_limit")


# ─── Rate Limiter ─────────────────────────────────────────────────────────────

async def check_rate_limit(identifier: str, limit: int, window_seconds: int = 60) -> tuple[bool, int]:
    """
    Sliding-window rate limiter.

    Args:
        identifier: Unique key (IP address, user ID, etc.)
        limit: Maximum allowed requests.
        window_seconds: Time window in seconds.

    Returns:
        (is_allowed, current_count)
    """
    key = f"rl:{identifier}"
    try:
        client = await get_redis_client()
        full_key = f"motomod:{key}"
        current = await client.incr(full_key)
        if current == 1:
            await client.expire(full_key, window_seconds)
        allowed = current <= limit
        return allowed, current
    except RedisError as e:
        logger.warning("rate_limit_check_error", identifier=identifier, error=str(e))
        return True, 0  # Fail open on Redis error
