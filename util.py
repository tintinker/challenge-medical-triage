import os
import redis
import json
import hashlib
from typing import Any, Optional


def retrieve_cache(
    redis_client: Optional[redis.Redis],
    cache_key_data: str,
) -> Optional[Any]:
    """
    Retrieve a value from cache.

    Args:
        redis_client: Redis client (can be None for no caching)
        cache_key_data: String to hash for the cache key

    Returns:
        The cached value if found, None otherwise

    Example:
        cached = retrieve_cache(self.redis, f"{self.model}|{case.age}|{case.symptoms}")
        if cached is not None:
            return cached, True
    """
    if not redis_client:
        return None

    cache_key = f"triage:{hashlib.md5(cache_key_data.encode()).hexdigest()}"

    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)  # type: ignore
    except Exception as e:
        print(f"Cache read error: {e}")

    return None


def store_cache(
    redis_client: Optional[redis.Redis],
    cache_key_data: str,
    result: Any,
    ttl: Optional[int] = None,
) -> None:
    """
    Store a value in cache.

    Args:
        redis_client: Redis client (can be None for no caching)
        cache_key_data: String to hash for the cache key
        result: The value to cache
        ttl: Time to live in seconds. If None, cache never expires

    Example:
        store_cache(self.redis, f"{self.model}|{case.age}", result, ttl=None)
    """
    if not redis_client:
        return

    cache_key = f"triage:{hashlib.md5(cache_key_data.encode()).hexdigest()}"

    try:
        if ttl is None:
            redis_client.set(cache_key, json.dumps(result))
        else:
            redis_client.setex(cache_key, ttl, json.dumps(result))
    except Exception as e:
        print(f"Cache write error: {e}")


def get_api_key_and_redis_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY environment variable")
        exit(1)

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    try:
        redis_client = redis.Redis(
            host=redis_host, port=redis_port, decode_responses=True
        )
        redis_client.ping()
        print(f"Connected to Redis at {redis_host}:{redis_port}")
    except Exception as e:
        print(f"Redis not available: {e}")
        print("Running without cache")
        redis_client = None

    return api_key, redis_client
