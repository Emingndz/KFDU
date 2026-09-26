from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.catalog.schemas import ContentSummary
from app.modules.users.schemas import PublicUserOut


class ReviewPreview(BaseModel):
    id: int
    excerpt: str
    is_truncated: bool
    has_spoiler: bool


class ListPreview(BaseModel):
    id: int
    title: str
    item_count: int
    cover_urls: list[str]


class CommentPreview(BaseModel):
    id: int
    author: PublicUserOut
    body: str


class ActivityOut(BaseModel):
    id: int
    card_type: str
    actor: PublicUserOut
    content: ContentSummary | None
    rating: int | None
    review: ReviewPreview | None
    status: str | None
    list: ListPreview | None
    created_at: datetime
    likes_count: int
    liked_by_me: bool
    comments_count: int
    comments_preview: list[CommentPreview]


class CommentOut(BaseModel):
    id: int
    activity_id: int
    author: PublicUserOut
    body: str
    created_at: datetime
    updated_at: datetime
    can_edit: bool
    can_delete: bool


class CommentCreateIn(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class CommentUpdateIn(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class NotificationOut(BaseModel):
    id: int
    type: str
    actor: PublicUserOut
    activity_id: int | None
    content: ContentSummary | None
    comment_excerpt: str | None
    is_read: bool
    created_at: datetime


class ReviewOut(BaseModel):
    id: int
    author: PublicUserOut
    content: ContentSummary | None
    body: str
    excerpt: str
    is_truncated: bool
    has_spoiler: bool
    rating: int | None
    created_at: datetime
    updated_at: datetime
    is_edited: bool
    activity_id: int | None
    likes_count: int
    liked_by_me: bool
    comments_count: int


class ReviewDetail(ReviewOut):
    content: ContentSummary
