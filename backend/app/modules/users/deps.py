from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.deps import DbSession
from app.core.errors import AppError
from app.core.security import decode_access_token
from app.modules.users.models import User

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

_UNAUTHENTICATED = AppError(
    401, "NOT_AUTHENTICATED", "Giriş yapman gerekiyor", headers={"WWW-Authenticate": "Bearer"}
)
_INVALID_TOKEN = AppError(
    401,
    "INVALID_TOKEN",
    "Oturumun geçersiz veya süresi dolmuş, tekrar giriş yap",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(db: DbSession, token: Annotated[str | None, Depends(_oauth2_scheme)]) -> User:
    if token is None:
        raise _UNAUTHENTICATED

    payload = decode_access_token(token)
    try:
        user_id = int(payload.get("sub", ""))
    except (TypeError, ValueError) as exc:
        raise _INVALID_TOKEN from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active or payload.get("tv") != user.token_version:
        raise _INVALID_TOKEN
    return user


def get_optional_user(db: DbSession, token: Annotated[str | None, Depends(_oauth2_scheme)]) -> User | None:
    if token is None:
        return None
    try:
        return get_current_user(db, token)
    except AppError:
        return None


CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
