from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.core.errors import register_exception_handlers
from app.core.http import close_http_client
from app.core.logging import setup_logging
from app.core.rate_limit import limiter
from app.modules.auth.router import router as auth_router


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    close_http_client()


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(
        title=settings.APP_NAME,
        generate_unique_id_function=lambda r: f"{r.tags[0]}-{r.name}" if r.tags else r.name,
        lifespan=_lifespan,
    )

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={"detail": "Çok fazla istek gönderdin, biraz sonra tekrar dene", "code": "RATE_LIMITED"},
        )

    media_dir = Path(settings.MEDIA_DIR)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_dir), name="media")

    app.include_router(auth_router, prefix=settings.API_PREFIX)

    @app.get(f"{settings.API_PREFIX}/health", tags=["system"], summary="Sağlık kontrolü")
    def health() -> dict:
        db_ok = True
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception:
            db_ok = False

        return {
            "status": "ok" if db_ok else "degraded",
            "db": db_ok,
            "tmdb": bool(settings.TMDB_API_KEY),
            "book_provider": settings.BOOK_PROVIDER,
            "llm": "enabled" if settings.NVIDIA_API_KEY else "disabled",
        }

    return app


app = create_app()
