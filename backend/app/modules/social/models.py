from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Activity(Base, TimestampMixin):
    __tablename__ = "activities"
    __table_args__ = (
        CheckConstraint("verb IN ('log', 'status', 'list_add', 'list_create')", name="verb_valid"),
        Index("ix_activities_actor_id", "actor_id", "id"),
        Index("ix_activities_content_id", "content_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    verb: Mapped[str] = mapped_column(String(20), nullable=False)
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id", ondelete="CASCADE"), default=None
    )
    list_id: Mapped[int | None] = mapped_column(ForeignKey("user_lists.id", ondelete="CASCADE"), default=None)
    status: Mapped[str | None] = mapped_column(String(12), default=None)


class ActivityLike(Base):
    __tablename__ = "activity_likes"

    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))


class ActivityComment(Base, TimestampMixin):
    __tablename__ = "activity_comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint("type IN ('follow', 'like', 'comment')", name="type_valid"),
        Index("ix_notifications_recipient_unread", "recipient_id", "is_read", "id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    activity_id: Mapped[int | None] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"), default=None
    )
    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("activity_comments.id", ondelete="CASCADE"), default=None
    )
    is_read: Mapped[bool] = mapped_column(nullable=False, default=False)
