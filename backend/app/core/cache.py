import threading
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from cachetools import TTLCache
from cachetools.keys import hashkey

_F = TypeVar("_F", bound=Callable[..., Any])

_caches: list[TTLCache] = []
_lock = threading.Lock()


def ttl_cache(ttl: float, maxsize: int = 512) -> Callable[[_F], _F]:
    def decorator(func: _F) -> _F:
        cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        _caches.append(cache)

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = hashkey(*args, **kwargs)
            with _lock:
                if key in cache:
                    return cache[key]
            result = func(*args, **kwargs)
            with _lock:
                cache[key] = result
            return result

        return wrapper  # type: ignore[return-value]

    return decorator


def clear_all_caches() -> None:
    with _lock:
        for cache in _caches:
            cache.clear()
