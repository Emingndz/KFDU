from collections import defaultdict
from collections.abc import Callable
from typing import Any

_handlers: dict[str, list[Callable[..., None]]] = defaultdict(list)


def subscribe(event: str, handler: Callable[..., None]) -> None:
    if handler not in _handlers[event]:
        _handlers[event].append(handler)


def emit(event: str, **payload: Any) -> None:
    for handler in _handlers[event]:
        handler(**payload)
