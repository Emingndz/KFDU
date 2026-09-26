from datetime import timedelta
from typing import Any
import random
import string
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api import deps
from app.core import security
from app.core.email import send_password_reset_email
from app.crud import crud_user
from app.schemas.token import Token
from app.schemas.user import PasswordResetRequest, PasswordResetConfirm, UserUpdate

router = APIRouter()

# In-memory storage for reset codes (use Redis in production)
password_reset_codes = {}


class CodeVerifyRequest(BaseModel):
    code: str


@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    # Try to authenticate with email first
    user = crud_user.get_user_by_email(db, email=form_data.username)
    # If not found by email, try username
    if not user:
        user = crud_user.get_user_by_username(db, username=form_data.username)
        
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email/username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=30)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/password-reset/request")
def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Request a password reset. Generates a 6-digit code and stores it.
    In production, this would send an email with the code.
    """
    user = crud_user.get_user_by_email(db, email=reset_request.email)
    if not user:
        # Don't reveal if user exists or not for security
        return {"message": "Eğer bu e-posta kayıtlıysa, şifre sıfırlama kodu gönderildi."}
    
    # Generate 6-digit code
    code = ''.join(random.choices(string.digits, k=6))
    
    # Store code with email (in production use Redis with expiration)
    password_reset_codes[code] = {
        "email": user.email,
        "used": False
    }
    
    # Send email with code
    email_sent = send_password_reset_email(user.email, code)
    
    return {
        "message": "Şifre sıfırlama kodu e-postanıza gönderildi." if email_sent else "Kod oluşturuldu (e-posta gönderilemedi).",
        "email_sent": email_sent
    }


@router.post("/password-reset/verify")
def verify_reset_code(
    verify_request: CodeVerifyRequest,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Verify the 6-digit reset code and return a token for password reset.
    """
    code = verify_request.code
    
    if code not in password_reset_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz veya süresi dolmuş kod"
        )
    
    code_data = password_reset_codes[code]
    
    if code_data["used"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu kod zaten kullanılmış"
        )
    
    # Mark code as used
    password_reset_codes[code]["used"] = True
    
    # Generate actual reset token
    reset_token = security.create_password_reset_token(code_data["email"])
    
    return {
        "valid": True,
        "token": reset_token,
        "message": "Kod doğrulandı. Yeni şifrenizi belirleyebilirsiniz."
    }


@router.post("/password-reset/confirm")
def confirm_password_reset(
    reset_confirm: PasswordResetConfirm,
    db: Session = Depends(deps.get_db)
) -> Any:
    """
    Confirm password reset with token and set new password.
    """
    email = security.verify_password_reset_token(reset_confirm.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Geçersiz veya süresi dolmuş token"
        )
    
    user = crud_user.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Kullanıcı bulunamadı"
        )
    
    # Update password
    user_update = UserUpdate(password=reset_confirm.new_password)
    crud_user.update_user(db, db_obj=user, obj_in=user_update)
    
    return {"message": "Şifreniz başarıyla güncellendi. Giriş yapabilirsiniz."}
