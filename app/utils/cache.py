# app/utils/cache.py

import json
import hashlib
import aioredis
from typing import Any, Optional
from app.config import get_settings

settings = get_settings()


class RedisCache:
    """
    Lightweight async Redis wrapper with JSON serialization,
    automatic key hashing, and graceful fallbacks.
    """

    def __init__(self):
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

        self.client = aioredis.from_url(
            redis_url,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

   
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
   
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """
        Store value in Redis with optional TTL (defaults to global config).
        """
        try:
            hashed_key = self.make_key(key)
            payload = json.dumps(value)
            expire_time = ttl or settings.CACHE_EXPIRE_SECONDS

            await self.client.set(hashed_key, payload, ex=expire_time)
        except Exception:
            pass

    async def test_connection(self) -> bool:
      try:
        pong = await self.client.ping()
        return pong
      except Exception:
        return False



redis_cache: RedisCache = RedisCache()

