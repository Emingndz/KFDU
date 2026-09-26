import re

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.modules.users.schemas import MeOut
from app.modules.users.validation import validate_username

_PASSWORD_HAS_LETTER = re.compile(r"[A-Za-z]")
_PASSWORD_HAS_DIGIT = re.compile(r"\d")


def _validate_password_strength(value: str) -> str:
    if not _PASSWORD_HAS_LETTER.search(value) or not _PASSWORD_HAS_DIGIT.search(value):
        raise ValueError("Şifre en az bir harf ve bir rakam içermeli")
    return value


class RegisterIn(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)
    password_confirm: str

    @field_validator("username")
    @classmethod
    def _username(cls, v: str) -> str:
        return validate_username(v)

    @field_validator("email")
    @classmethod
    def _email_lower(cls, v: str) -> str:
        return v.lower()

    @field_validator("password")
    @classmethod
    def _password(cls, v: str) -> str:
        return _validate_password_strength(v)

    @model_validator(mode="after")
    def _passwords_match(self) -> "RegisterIn":
        if self.password != self.password_confirm:
            raise ValueError("Şifreler eşleşmiyor")
        return self


class LoginIn(BaseModel):
    login: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: MeOut


class ResetRequestIn(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def _email_lower(cls, v: str) -> str:
        return v.lower()


class ResetVerifyIn(BaseModel):
    email: EmailStr
    code: str

    @field_validator("email")
    @classmethod
    def _email_lower(cls, v: str) -> str:
        return v.lower()


class ResetConfirmIn(BaseModel):
    email: EmailStr
    code: str
    new_password: str = Field(min_length=8, max_length=255)
    new_password_confirm: str

    @field_validator("email")
    @classmethod
    def _email_lower(cls, v: str) -> str:
        return v.lower()

    @field_validator("new_password")
    @classmethod
    def _password(cls, v: str) -> str:
        return _validate_password_strength(v)

    @model_validator(mode="after")
    def _passwords_match(self) -> "ResetConfirmIn":
        if self.new_password != self.new_password_confirm:
            raise ValueError("Şifreler eşleşmiyor")
        return self


class ChangePasswordIn(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=255)
    new_password_confirm: str

    @field_validator("new_password")
    @classmethod
    def _password(cls, v: str) -> str:
        return _validate_password_strength(v)

    @model_validator(mode="after")
    def _passwords_match(self) -> "ChangePasswordIn":
        if self.new_password != self.new_password_confirm:
            raise ValueError("Şifreler eşleşmiyor")
        return self
