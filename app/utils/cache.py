# app/utils/cache.py

import json
import hashlib
from typing import Any, Optional
from redis import asyncio as aioredis
from app.config import get_settings

settings = get_settings()

class RedisCache:
    """
    Lightweight async Redis wrapper with JSON serialization,
    automatic key hashing, and graceful fallbacks.
    Uses redis-py with asyncio support.
    """

    def __init__(self):
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        
        self.client = aioredis.Redis.from_url(
            redis_url,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )
        self._is_connected = False

    # Helpers
    @staticmethod
    def make_key(raw_key: str) -> str:
        """
        Hash keys to avoid extremely long Redis keys
        (especially for prompts or JSON inputs).
        """
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        return f"cache:{key_hash}"

    # GET
    async def get(self, key: str) -> Optional[Any]:
        """
        Fetch cached value from Redis.
        Returns None if key does not exist or Redis is unavailable.
        """
        try:
            hashed_key = self.make_key(key)
            data = await self.client.get(hashed_key)
            if data:
                return json.loads(data)
        except Exception:
            # Allow system to continue even if Redis goes down
            return None
        return None

    # SET
    async def set(self, key: str, value: Any, expire: int = None) -> None:
        """
        Store value in Redis with optional expire time in seconds.
        Uses global CACHE_EXPIRE_SECONDS if not specified.
        """
        try:
            hashed_key = self.make_key(key)
            payload = json.dumps(value)
            expire_time = expire if expire is not None else settings.CACHE_EXPIRE_SECONDS
            
            await self.client.set(
                name=hashed_key,
                value=payload,
                ex=expire_time
            )
        except Exception:
            # Silently fail if Redis is unavailable
            pass

    async def test_connection(self) -> bool:
        """Test if Redis connection is working."""
        try:
            return await self.client.ping()
        except Exception:
            return False

    async def close(self):
        """Close the Redis connection."""
        await self.client.close()

# Create a single instance of the cache
redis_cache = RedisCache()