import logging
import re
import time

import httpx

from app.core.config import settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)

_client: httpx.Client | None = None


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
    max_attempts = 2
    for attempt in range(1, max_attempts + 1):
        try:
            response = client.request(method, url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
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
