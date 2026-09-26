from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.catalog.schemas import ContentSummary, ContentType
from app.modules.users.schemas import PublicUserOut


class ListCreateIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_public: bool = True


class ListUpdateIn(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    is_public: bool | None = None


class ListItemIn(BaseModel):
    type: ContentType
    external_id: str
    note: str | None = Field(default=None, max_length=300)


class ListItemNoteIn(BaseModel):
    note: str | None = Field(default=None, max_length=300)


class ReorderIn(BaseModel):
    content_ids: list[int]


class ListOut(BaseModel):
    id: int
    owner: PublicUserOut
    title: str
    description: str | None
    is_public: bool
    item_count: int
    cover_urls: list[str]
    created_at: datetime
    updated_at: datetime


class ListItemOut(BaseModel):
    content: ContentSummary
    note: str | None
    position: int
    added_at: datetime


class ListDetail(ListOut):
    items: list[ListItemOut]


class MyListOut(ListOut):
    contains: bool
