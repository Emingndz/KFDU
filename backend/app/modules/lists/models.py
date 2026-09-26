from datetime import UTC, datetime

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class UserList(Base, TimestampMixin):
    __tablename__ = "user_lists"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), default=None)
    is_public: Mapped[bool] = mapped_column(nullable=False, default=True)


class ListItem(Base):
    __tablename__ = "list_items"
    __table_args__ = (Index("ix_list_items_list_position", "list_id", "position"),)

    list_id: Mapped[int] = mapped_column(ForeignKey("user_lists.id", ondelete="CASCADE"), primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id", ondelete="CASCADE"), primary_key=True)
    position: Mapped[int] = mapped_column(nullable=False)
    note: Mapped[str | None] = mapped_column(String(300), default=None)
    added_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
