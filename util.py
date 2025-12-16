import os
import json
import hashlib
from typing import Any, Optional, Dict
from pathlib import Path


def retrieve_cache(
    cache_data: Optional[Dict],
    cache_key_data: str,
) -> Optional[Any]:
    """
    Retrieve a value from cache.

    Args:
        cache_data: Dictionary containing cache data (can be None for no caching)
        cache_key_data: String to hash for the cache key

    Returns:
        The cached value if found, None otherwise

    Example:
        cached = retrieve_cache(self.cache, f"{self.model}|{case.age}|{case.symptoms}")
        if cached is not None:
            return cached, True
    """
    if not cache_data:
        return None

    cache_key = f"triage:{hashlib.md5(cache_key_data.encode()).hexdigest()}"

    try:
        return cache_data.get(cache_key)
    except Exception as e:
        print(f"Cache read error: {e}")

    return None


def store_cache(
    cache_data: Optional[Dict],
    cache_key_data: str,
    result: Any,
    ttl: Optional[int] = None,
) -> None:
    """
    Store a value in cache.

    Args:
        cache_data: Dictionary containing cache data (can be None for no caching)
        cache_key_data: String to hash for the cache key
        result: The value to cache
        ttl: Time to live in seconds (ignored for file-based cache)

    Example:
        store_cache(self.cache, f"{self.model}|{case.age}", result, ttl=None)
    """
    if not cache_data:
        return

    cache_key = f"triage:{hashlib.md5(cache_key_data.encode()).hexdigest()}"

    try:
        cache_data[cache_key] = result
    except Exception as e:
        print(f"Cache write error: {e}")


def load_cache_from_file(cache_file: str = "cache.json") -> Optional[Dict]:
    """
    Load cache from a JSON file.

    Args:
        cache_file: Path to the cache file

    Returns:
        Dictionary containing cache data, or None if file doesn't exist
    """
    cache_path = Path(cache_file)
    if not cache_path.exists():
        print(f"Cache file {cache_file} not found")
        return None

    try:
        with open(cache_path, "r") as f:
            cache_data = json.load(f)
        print(f"Loaded cache from {cache_file} ({len(cache_data)} entries)")
        return cache_data
    except Exception as e:
        print(f"Error loading cache file: {e}")
        return None


def get_api_key_and_cache():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY environment variable")
        exit(1)

    cache_data = load_cache_from_file("cache.json")

    return api_key, cache_data
