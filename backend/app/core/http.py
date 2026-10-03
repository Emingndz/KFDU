import logging
import re
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from contextvars import ContextVar

import httpx

from app.core.config import settings
from app.core.errors import AppError, not_found

logger = logging.getLogger(__name__)

_client: httpx.Client | None = None


class _Throttle:
    """Ardışık istekler arasında en az 1/per_second saniye bırakır."""

    def __init__(
        self,
        per_second: float,
        *,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._interval = 1.0 / per_second
        self._clock = clock
        self._sleep = sleep
        self._next_at = 0.0

    def wait(self) -> None:
        now = self._clock()
        if now < self._next_at:
            self._sleep(self._next_at - now)
            now = self._next_at
        self._next_at = now + self._interval


_throttle: ContextVar[_Throttle | None] = ContextVar("http_throttle", default=None)


@contextmanager
def throttled(per_second: float) -> Iterator[None]:
    """Blok içindeki dış istekleri saniyede en fazla `per_second` ile sınırlar.

    ContextVar olduğu için yalnız bloğu çalıştıran iş (ör. arka plandaki toplu içe aktarma) yavaşlar;
    aynı anda sunulan diğer API isteklerinin dış çağrıları etkilenmez.
    """
    token = _throttle.set(_Throttle(per_second))
    try:
        yield
    finally:
        _throttle.reset(token)


class ExternalServiceError(AppError):
    def __init__(self, service: str) -> None:
        message = f"{service} şu anda yanıt vermiyor, biraz sonra tekrar dene"
        super().__init__(502, "EXTERNAL_SERVICE_ERROR", message)


def get_http_client() -> httpx.Client:
    global _client
    if _client is None:
        _client = httpx.Client(
            timeout=httpx.Timeout(10.0, connect=5.0),
            headers={"User-Agent": f"KFDU/2.0 (+{settings.CONTACT_EMAIL})"},
        )
    return _client


def close_http_client() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


_SECRET_PARAM_RE = re.compile(r"([?&](?:api_key|key)=)[^&]+", re.IGNORECASE)


def _masked(url: str) -> str:
    return _SECRET_PARAM_RE.sub(r"\1***", url)


def request_json(
    method: str,
    url: str,
    *,
    params: dict[str, object] | None = None,
    headers: dict[str, str] | None = None,
    service: str = "Dış servis",
) -> dict:
    client = get_http_client()
    throttle = _throttle.get()
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        if throttle is not None:
            throttle.wait()
        try:
            response = client.request(method, url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise not_found(f"{service} içinde bulunamadı") from exc
            if exc.response.status_code != 429 and exc.response.status_code < 500:
                raise
            if attempt == max_attempts:
                logger.warning("%s yanıt vermedi: %s", service, _masked(str(url)))
                raise ExternalServiceError(service) from exc
        except httpx.HTTPError as exc:
            if attempt == max_attempts:
                logger.warning("%s bağlantı hatası: %s", service, _masked(str(url)))
                raise ExternalServiceError(service) from exc
        time.sleep(0.5)
    raise ExternalServiceError(service)
