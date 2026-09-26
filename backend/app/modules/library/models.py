from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class LibraryEntry(Base, TimestampMixin):
    __tablename__ = "library_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="uq_library_entries_user_content"),
        CheckConstraint("status IN ('completed', 'in_progress', 'planned', 'dropped')", name="status_valid"),
        CheckConstraint("rating BETWEEN 1 AND 10", name="rating_range"),
        Index("ix_library_entries_content_rating", "content_id", "rating"),
        Index("ix_library_entries_user_status", "user_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str | None] = mapped_column(String(12), default=None)
    rating: Mapped[int | None] = mapped_column(SmallInteger, default=None)
    is_favorite: Mapped[bool] = mapped_column(nullable=False, default=False)
    progress: Mapped[int | None] = mapped_column(default=None)
    started_at: Mapped[date | None] = mapped_column(Date, default=None)
    finished_at: Mapped[date | None] = mapped_column(Date, default=None)
    rated_at: Mapped[datetime | None] = mapped_column(default=None)


class Review(Base, TimestampMixin):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "content_id", name="uq_reviews_user_content"),
        Index("ix_reviews_content_created", "content_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    has_spoiler: Mapped[bool] = mapped_column(nullable=False, default=False)
