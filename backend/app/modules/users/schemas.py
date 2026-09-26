from datetime import datetime

from pydantic import BaseModel, ConfigDict


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
