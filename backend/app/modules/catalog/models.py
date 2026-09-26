from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Content(Base, TimestampMixin):
    __tablename__ = "contents"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_contents_source_external"),
        CheckConstraint("type IN ('movie', 'tv', 'book')", name="type_valid"),
        CheckConstraint("source IN ('tmdb', 'openlibrary', 'google_books')", name="source_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    external_id: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    original_title: Mapped[str | None] = mapped_column(String(500), default=None)
    year: Mapped[int | None] = mapped_column(index=True, default=None)
    poster_url: Mapped[str | None] = mapped_column(String(500), default=None)
    backdrop_url: Mapped[str | None] = mapped_column(String(500), default=None)
    overview: Mapped[str | None] = mapped_column(Text, default=None)
    genres: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    people: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    runtime_minutes: Mapped[int | None] = mapped_column(default=None)
    page_count: Mapped[int | None] = mapped_column(default=None)
    seasons: Mapped[int | None] = mapped_column(default=None)
    original_language: Mapped[str | None] = mapped_column(String(10), default=None)
    external_rating: Mapped[float | None] = mapped_column(default=None)
    external_votes: Mapped[int | None] = mapped_column(default=None)
    extra: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    fetched_at: Mapped[datetime | None] = mapped_column(default=None)
