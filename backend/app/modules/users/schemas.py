from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.genres import GENRE_KEYS
from app.modules.users.validation import validate_username


class PublicUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str | None
    avatar_url: str | None
    bio: str | None


class MeOut(PublicUserOut):
    email: str
    favorite_genres: list[str]
    created_at: datetime


class PublicUserWithFollowOut(PublicUserOut):
    is_following: bool


class ProfileOut(PublicUserOut):
    created_at: datetime
    followers_count: int
    following_count: int
    is_following: bool
    follows_me: bool
    is_me: bool


def _validate_genres(value: list[str] | None) -> list[str] | None:
    if value is None:
        return value
    unknown = sorted(set(value) - GENRE_KEYS)
    if unknown:
        raise ValueError(f"Geçersiz tür anahtarı: {', '.join(unknown)}")
    return value


class MeUpdateIn(BaseModel):
    display_name: str | None = Field(default=None, max_length=50)
    bio: str | None = Field(default=None, max_length=300)
    username: str | None = None
    favorite_genres: list[str] | None = None

    @field_validator("username")
    @classmethod
    def _username(cls, v: str | None) -> str | None:
        return validate_username(v) if v is not None else v

    @field_validator("favorite_genres")
    @classmethod
    def _genres(cls, v: list[str] | None) -> list[str] | None:
        return _validate_genres(v)


class EmailChangeIn(BaseModel):
    new_email: EmailStr
    current_password: str

    @field_validator("new_email")
    @classmethod
    def _email_lower(cls, v: str) -> str:
        return v.lower()


class DeleteAccountIn(BaseModel):
    password: str
