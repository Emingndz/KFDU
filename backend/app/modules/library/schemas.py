from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.modules.catalog.schemas import ContentSummary, ContentType
from app.modules.users.schemas import PublicUserOut


class LibraryStatus(StrEnum):
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    PLANNED = "planned"
    DROPPED = "dropped"


class EntryUpdateIn(BaseModel):
    status: LibraryStatus | None = None
    rating: int | None = Field(default=None, ge=1, le=10)
    is_favorite: bool | None = None
    progress: int | None = Field(default=None, ge=0)


class EntryOut(BaseModel):
    content: ContentSummary
    status: LibraryStatus | None
    rating: int | None
    is_favorite: bool
    progress: int | None
    started_at: date | None
    finished_at: date | None
    updated_at: datetime


class PlatformStats(BaseModel):
    average: float | None
    count: int
    distribution: dict[int, int]


class MeState(BaseModel):
    entry: EntryOut | None
    review_id: int | None


class FriendEntry(BaseModel):
    user: PublicUserOut
    rating: int | None
    status: LibraryStatus | None


class ContentState(BaseModel):
    content_id: int
    platform: PlatformStats
    me: MeState | None
    friends: list[FriendEntry]


class LookupIn(BaseModel):
    keys: list[str] = Field(max_length=60)


class LookupEntryOut(BaseModel):
    status: LibraryStatus | None
    rating: int | None
    is_favorite: bool


class ReviewCreateIn(BaseModel):
    type: ContentType
    external_id: str
    body: str = Field(min_length=3, max_length=5000)
    has_spoiler: bool = False


class ReviewUpdateIn(BaseModel):
    body: str | None = Field(default=None, min_length=3, max_length=5000)
    has_spoiler: bool | None = None


class ReviewBasicOut(BaseModel):
    id: int
    body: str
    has_spoiler: bool
    created_at: datetime
    updated_at: datetime
