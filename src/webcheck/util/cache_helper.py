from pathlib import Path

from webcheck.conf import WEBCHECK_CACHE_ENGINE, WEBCHECK_DATA_DIR


def get_redis_cache_client():
    pass


def read_from_redis_cache(r, key):
    pass


def write_to_redis_cache(r, key, value, ttl):
    pass


def read_from_local_cache(key) -> str | None:
    cache_file = Path(WEBCHECK_DATA_DIR) / "cache" / f"{key}.cache"
    if not cache_file.exists():
        return None
    try:
        with open(cache_file, "r") as f:
            return f.read()
    except Exception:
        print(f"Failed to read cache file: {cache_file}")
        return None


def write_to_local_cache(key, value, ttl=30) -> None:
    cache_file = Path(WEBCHECK_DATA_DIR) / "cache" / f"{key}.cache"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_file, "w") as f:
            f.write(value)
    except Exception:
        print(f"Failed to write cache file: {cache_file}")
        pass


def cache_read(key) -> str | None:
    if WEBCHECK_CACHE_ENGINE == "local":
        return read_from_local_cache(key)
    elif WEBCHECK_CACHE_ENGINE == "redis":
        r = get_redis_cache_client()
        return read_from_redis_cache(r, key)
    else:
        return None


def cache_write(key, value, ttl=30) -> None:
    if WEBCHECK_CACHE_ENGINE == "local":
        write_to_local_cache(key, value, ttl)
    elif WEBCHECK_CACHE_ENGINE == "redis":
        r = get_redis_cache_client()
        write_to_redis_cache(r, key, value, ttl)
    else:
        pass
