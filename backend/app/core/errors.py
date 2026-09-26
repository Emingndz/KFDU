import logging
import re
from collections.abc import Callable

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def bad_request(code: str, message: str) -> AppError:
    return AppError(status.HTTP_400_BAD_REQUEST, code, message)


def not_found(message: str = "Kayıt bulunamadı") -> AppError:
    return AppError(status.HTTP_404_NOT_FOUND, "NOT_FOUND", message)


def forbidden(message: str = "Bu işlem için yetkin yok") -> AppError:
    return AppError(status.HTTP_403_FORBIDDEN, "FORBIDDEN", message)


def conflict(code: str, message: str) -> AppError:
    return AppError(status.HTTP_409_CONFLICT, code, message)


_PATTERN_TRANSLATIONS: list[tuple[re.Pattern[str], Callable[[re.Match[str]], str]]] = [
    (re.compile(r"^Field required$"), lambda m: "Bu alan zorunlu"),
    (
        re.compile(r"^String should have at least (\d+) characters?$"),
        lambda m: f"En az {m.group(1)} karakter olmalı",
    ),
    (
        re.compile(r"^String should have at most (\d+) characters?$"),
        lambda m: f"En fazla {m.group(1)} karakter olabilir",
    ),
    (
        re.compile(r"^Input should be greater than or equal to (-?\d+)$"),
        lambda m: f"En az {m.group(1)} olmalı",
    ),
    (
        re.compile(r"^Input should be less than or equal to (-?\d+)$"),
        lambda m: f"En fazla {m.group(1)} olabilir",
    ),
    (re.compile(r"^value is not a valid email address.*$"), lambda m: "Geçerli bir e-posta adresi girin"),
]


def _translate_message(message: str) -> str:
    for pattern, build in _PATTERN_TRANSLATIONS:
        match = pattern.match(message)
        if match:
            return build(match)
    return message


_STATUS_CODES = {
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_405_METHOD_NOT_ALLOWED: "METHOD_NOT_ALLOWED",
}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.message, "code": exc.code})

    @app.exception_handler(RequestValidationError)
    async def _validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        errors = [
            {
                "field": ".".join(str(p) for p in err["loc"] if p != "body"),
                "message": _translate_message(err["msg"]),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "detail": "Lütfen form alanlarını kontrol edin",
                "code": "VALIDATION_ERROR",
                "errors": errors,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = _STATUS_CODES.get(exc.status_code, "HTTP_ERROR")
        detail = exc.detail if isinstance(exc.detail, str) else "Bir hata oluştu"
        return JSONResponse(status_code=exc.status_code, content={"detail": detail, "code": code})

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Beklenmeyen hata: %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Beklenmeyen bir hata oluştu", "code": "INTERNAL_ERROR"},
        )
