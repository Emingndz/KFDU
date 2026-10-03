from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class ImportJob(Base, TimestampMixin):
    __tablename__ = "import_jobs"
    __table_args__ = (
        CheckConstraint("source IN ('letterboxd', 'goodreads')", name="source_valid"),
        CheckConstraint("status IN ('pending', 'running', 'done', 'failed')", name="status_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="pending")
    total: Mapped[int] = mapped_column(nullable=False, default=0)
    processed: Mapped[int] = mapped_column(nullable=False, default=0)
    matched: Mapped[int] = mapped_column(nullable=False, default=0)
    report: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    error: Mapped[str | None] = mapped_column(Text, default=None)
    finished_at: Mapped[datetime | None] = mapped_column(default=None)
