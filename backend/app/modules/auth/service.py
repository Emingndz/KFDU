import hmac
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from fastapi import BackgroundTasks
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.email import send_email
from app.core.errors import AppError, bad_request, conflict
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.models import PasswordResetCode
from app.modules.users.models import User

RESET_CODE_TTL_MINUTES = 15
RESET_CODE_MAX_REQUESTS_PER_WINDOW = 3
RESET_CODE_MAX_ATTEMPTS = 5


def _code_hash(code: str) -> str:
    return sha256(f"{code}{settings.SECRET_KEY}".encode()).hexdigest()


def register(db: Session, *, username: str, email: str, password: str) -> User:
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise conflict("EMAIL_TAKEN", "Bu e-posta zaten kullanımda")
    if db.scalar(select(User).where(User.username == username)) is not None:
        raise conflict("USERNAME_TAKEN", "Bu kullanıcı adı alınmış")

    user = User(username=username, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, *, login: str, password: str) -> User:
    identifier = login.lower()
    user = db.scalar(select(User).where((User.email == identifier) | (User.username == identifier)))
    if user is None:
        raise AppError(401, "INVALID_CREDENTIALS", "E-posta/kullanıcı adı veya şifre hatalı")

    valid, new_hash = verify_password(password, user.password_hash)
    if not valid:
        raise AppError(401, "INVALID_CREDENTIALS", "E-posta/kullanıcı adı veya şifre hatalı")
    if not user.is_active:
        raise AppError(403, "USER_INACTIVE", "Hesabın devre dışı bırakılmış")

    if new_hash is not None:
        user.password_hash = new_hash
        db.commit()

    return user


def request_password_reset(db: Session, *, email: str, background_tasks: BackgroundTasks) -> None:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if user is None:
        return

    window_start = datetime.now(UTC) - timedelta(minutes=RESET_CODE_TTL_MINUTES)
    recent_count = db.scalar(
        select(func.count())
        .select_from(PasswordResetCode)
        .where(PasswordResetCode.user_id == user.id, PasswordResetCode.created_at >= window_start)
    )
    if recent_count is not None and recent_count >= RESET_CODE_MAX_REQUESTS_PER_WINDOW:
        return

    db.execute(
        update(PasswordResetCode)
        .where(PasswordResetCode.user_id == user.id, PasswordResetCode.used_at.is_(None))
        .values(used_at=datetime.now(UTC))
    )

    code = f"{secrets.randbelow(10**6):06d}"
    db.add(
        PasswordResetCode(
            user_id=user.id,
            code_hash=_code_hash(code),
            expires_at=datetime.now(UTC) + timedelta(minutes=RESET_CODE_TTL_MINUTES),
        )
    )
    db.commit()

    background_tasks.add_task(
        send_email,
        user.email,
        "KFDU şifre sıfırlama kodun",
        f"Şifre sıfırlama kodun: {code}\nBu kod {RESET_CODE_TTL_MINUTES} dakika geçerlidir.",
    )


def _get_latest_valid_code(db: Session, user: User) -> PasswordResetCode | None:
    return db.scalar(
        select(PasswordResetCode)
        .where(
            PasswordResetCode.user_id == user.id,
            PasswordResetCode.used_at.is_(None),
            PasswordResetCode.expires_at > datetime.now(UTC),
        )
        .order_by(PasswordResetCode.created_at.desc())
        .limit(1)
    )


def _validate_reset_code(db: Session, *, email: str, code: str) -> PasswordResetCode:
    user = db.scalar(select(User).where(User.email == email.lower()))
    reset_code = _get_latest_valid_code(db, user) if user is not None else None
    if reset_code is None:
        raise bad_request("INVALID_CODE", "Kod hatalı veya süresi dolmuş")
    if reset_code.attempts >= RESET_CODE_MAX_ATTEMPTS:
        raise AppError(429, "TOO_MANY_ATTEMPTS", "Çok fazla hatalı deneme yaptın, yeni kod iste")
    if not hmac.compare_digest(reset_code.code_hash, _code_hash(code)):
        reset_code.attempts += 1
        db.commit()
        raise bad_request("INVALID_CODE", "Kod hatalı veya süresi dolmuş")
    return reset_code


def verify_password_reset(db: Session, *, email: str, code: str) -> None:
    _validate_reset_code(db, email=email, code=code)


def confirm_password_reset(db: Session, *, email: str, code: str, new_password: str) -> None:
    reset_code = _validate_reset_code(db, email=email, code=code)
    user = db.get(User, reset_code.user_id)
    user.password_hash = hash_password(new_password)
    user.token_version += 1
    reset_code.used_at = datetime.now(UTC)
    db.commit()


def change_password(db: Session, *, user: User, current_password: str, new_password: str) -> str:
    valid, _ = verify_password(current_password, user.password_hash)
    if not valid:
        raise bad_request("INVALID_PASSWORD", "Mevcut şifren yanlış")
    user.password_hash = hash_password(new_password)
    user.token_version += 1
    db.commit()
    return create_access_token(user.id, user.token_version)


def logout_all(db: Session, *, user: User) -> None:
    user.token_version += 1
    db.commit()
