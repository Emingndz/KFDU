from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.deps import DbSession
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.modules.auth import service
from app.modules.auth.schemas import (
    ChangePasswordIn,
    LoginIn,
    RegisterIn,
    ResetConfirmIn,
    ResetRequestIn,
    ResetVerifyIn,
    TokenOut,
)
from app.modules.users.deps import CurrentUser
from app.modules.users.schemas import MeOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_out(user) -> TokenOut:
    token = create_access_token(user.id, user.token_version)
    return TokenOut(access_token=token, user=MeOut.model_validate(user))


@router.post("/register", response_model=TokenOut, status_code=201, summary="Kayıt ol")
def register(payload: RegisterIn, db: DbSession) -> TokenOut:
    user = service.register(db, username=payload.username, email=payload.email, password=payload.password)
    return _token_out(user)


@router.post("/login", response_model=TokenOut, summary="Giriş yap")
@limiter.limit("10/minute")
def login(request: Request, payload: LoginIn, db: DbSession) -> TokenOut:
    user = service.login(db, login=payload.login, password=payload.password)
    return _token_out(user)


@router.post("/token", response_model=TokenOut, summary="Swagger için OAuth2 girişi")
def token_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
) -> TokenOut:
    user = service.login(db, login=form_data.username, password=form_data.password)
    return _token_out(user)


@router.post("/password-reset/request", status_code=202, summary="Şifre sıfırlama kodu iste")
@limiter.limit("10/hour")
def request_password_reset(
    request: Request, payload: ResetRequestIn, db: DbSession, background_tasks: BackgroundTasks
) -> dict:
    service.request_password_reset(db, email=payload.email, background_tasks=background_tasks)
    return {"detail": "Eğer bu e-posta kayıtlıysa sıfırlama kodu gönderildi."}


@router.post("/password-reset/verify", summary="Sıfırlama kodunu doğrula")
def verify_password_reset(payload: ResetVerifyIn, db: DbSession) -> dict:
    service.verify_password_reset(db, email=payload.email, code=payload.code)
    return {"valid": True}


@router.post("/password-reset/confirm", summary="Şifreyi sıfırla")
def confirm_password_reset(payload: ResetConfirmIn, db: DbSession) -> dict:
    service.confirm_password_reset(
        db, email=payload.email, code=payload.code, new_password=payload.new_password
    )
    return {"detail": "Şifren güncellendi, şimdi giriş yapabilirsin."}


@router.post("/change-password", response_model=TokenOut, summary="Şifreni değiştir")
def change_password(payload: ChangePasswordIn, user: CurrentUser, db: DbSession) -> TokenOut:
    token = service.change_password(
        db, user=user, current_password=payload.current_password, new_password=payload.new_password
    )
    return TokenOut(access_token=token, user=MeOut.model_validate(user))


@router.post("/logout-all", status_code=204, summary="Tüm cihazlardan çıkış yap")
def logout_all(user: CurrentUser, db: DbSession) -> None:
    service.logout_all(db, user=user)
